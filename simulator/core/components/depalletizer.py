from typing import Tuple, Optional
from simulator.core.components.component import Component
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.orders.order import OrderStatus, RefillOrder
from simulator.config import PALLET_BUFFER_PROCESS_TIME, ITEM_PROCESS_TIME, DEPALLETIZING_DELAY
import simpy
from simulator.gui.event_bus import EventBus
from simulator.gui.component_items import PALLET_ORDER_STATES


class Depalletizer(Component):
    """
    Unloads items from pallets and transitions items to other processes.
    Always connected to two outputs: empty pallet conveyor and batch builder.
    Can unload one item at a time onto batch builder
    After depalletizing process has been finished the depalletizer unloads the empty pallet forward.

    Additional Attributes
    ----------
    process_depal : simpy.Process
        SimPy process instance main depalletizing loop.
    coordinate : Tuple[int,int]
        Physical location of the depalletizer.
    pallet_process_time : float
        Time in simulation units to unload a pallet.
    item_process_time : float
        Time in simulation units to unload an item.
    start_delay : float
        Time in simulation units for the delay before the depalletizing starts.
    buffer : PayloadBuffer
        Buffer for holding pallets to process.
    current_item_id : int
        The id of the currently processed item.
    remaining_qty : int
        The amount of items there are left to process.
    """
    def __init__(self, env: simpy.Environment, depalletizer_id: str,
                 coordinate: Tuple[int,int],
                 pallet_process_time: float = PALLET_BUFFER_PROCESS_TIME,
                 item_process_time: float = ITEM_PROCESS_TIME,
                 start_delay: float = DEPALLETIZING_DELAY):
        super().__init__(env, component_id=depalletizer_id, static_process_time=pallet_process_time)
        self.process_depal = env.process(self._depal_loop())
        self._coordinate = coordinate
        self._pallet_process_time = pallet_process_time
        self._item_process_time = item_process_time
        self._start_delay = start_delay

        # Internal pallet buffer
        self._buffer = PayloadBuffer(env=env,
                                     buffer_id=f"{depalletizer_id}_buf",
                                     coordinate=coordinate,
                                     process_time=pallet_process_time)

        self._current_item_id: Optional[int] = None
        self._remaining_qty: Optional[int] = None

    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> Tuple[int,int]:
        return self._coordinate

    @property
    def buffer(self) -> PayloadBuffer:
        return self._buffer

    @property
    def payload(self) -> Optional[SystemPallet]:
        return self._buffer.payload

    @property
    def current_item_id(self) -> int:
        return self._current_item_id

    @property
    def remaining_qty(self) -> int:
        return self._remaining_qty

    # --------
    #  Logic
    # --------

    def connect(self, component: "Component", port: str = "out"):
        """
        Override base connect.
        If connecting pallet flow, delegate to internal buffer.
        Otherwise, connect normally (e.g., item conveyor).
        """
        if port in ("pallet_out", "out"):
            # pallet output → goes through buffer
            self._buffer.connect(component, port="out")
        elif port == "item_out":
            # item output → direct from depalletizer
            self._output = component
        else:
            # fallback: use base logic
            super().connect(component, port)

    def inject_event_bus(self, event_bus: EventBus):
        """
        Override base event bus injection.
        Delegate to internal buffer.
        """
        self.event_bus = event_bus
        self._buffer.event_bus = event_bus

    def current_process_time_left(self) -> float:
        """Calculate the expected time to left process the current order."""
        if self.payload is None:
            return 0.0

        item_time = self._remaining_qty * self._item_process_time
        total_time = item_time + self._pallet_process_time
        return total_time

    def can_load(self) -> bool:
        return self._buffer.can_load()

    def load(self, pallet: SystemPallet):
        """Route pallet through buffer first."""
        if self.can_load():
            self._buffer.load(pallet)

    def _handoff_pallet(self):
        """Empty pallet leaves via buffer handoff."""
        yield from self._buffer.handoff()

    def _process_item(self, item_id: int):
        """Load item on batch builder."""
        if self._output is not None:
            yield self.env.timeout(self._item_process_time)
            return self._output.load(item_id) # Indicate loading success
        return False

    def _depal_loop(self):
        """Main depalletizing loop."""
        while True:
            self._buffer.on_load_event = self.env.event()
            pallet = yield self._buffer.on_load_event  # wait for pallet

            if pallet is None:
                # Wait until a pallet exists
                yield self.env.timeout(0)
                continue

            # Init order info
            order = pallet.order
            if isinstance(order, RefillOrder):
                self._current_item_id = order.item_id
                self._remaining_qty = order.qty

            yield self.env.timeout(DEPALLETIZING_DELAY)  # Add a little delay before depalletizing is started
            print(f"[{self.env.now}] {self}: Started depalletizing {pallet.order}")

            # Process items
            if self.event_bus is not None:
                self.event_bus.emit("depalletizer_operating", {"id":self._component_id})

            while self._remaining_qty > 0:
                success = yield self.env.process(self._process_item(self._current_item_id))
                if not success:
                    # Try processing item until successful
                    continue
                self._remaining_qty -= 1
            self._current_item_id = None

            # Mark order done, clear pallet
            order.status = OrderStatus.COMPLETED
            print(f"[{self.env.now}] {self}: Depalletized {order}")
            pallet.clear_order()

            if self.event_bus is not None:
                self.event_bus.emit("update_payload_state", {"id": pallet.id, "state": PALLET_ORDER_STATES["Empty"]})
                self.event_bus.emit("depalletizer_idle", {"id":self._component_id})

            # Send empty pallet downstream
            yield self.env.process(self._handoff_pallet())