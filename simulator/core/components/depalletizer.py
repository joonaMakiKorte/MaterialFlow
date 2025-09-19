from typing import Tuple, Optional
from simulator.core.components.component import Component
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.orders.order import OrderStatus, RefillOrder
from simulator.config import BUFFER_PROCESS_TIME, ITEM_PROCESS_TIME

import simpy

class Depalletizer(Component):
    """
    Unloads items from pallets and transitions items to other processes.
    Always connected to two outputs: empty pallet conveyor and item conveyor.
    Can unload one item at a time onto an item conveyor infeed.
    After depalletizing process has been finished the depalletizer unloads the empty pallet forward.

    Additional Attributes
    ----------
    process : simpy.Process
        SimPy process instance for
        +this component.
    coordinate : Tuple[float,float]
        Physical location of the depalletizer.
    item_process_time : float
        Time in simulation units per movement cycle (processing delay for one item).
    pallet_unload_time : float
        Time in simulation units to unload a pallet.
    payload : SystemPallet
        SystemPallet occupying the depalletizer.
    current_item_id : int
        The id of the currently processed item.
    remaining_qty : int
        The amount of items there are left to process.
    on_load_event : simpy.events.Event
        Event to trigger depalletizing process on loading.
    """
    def __init__(self, env: simpy.Environment, depalletizer_id: int, coordinate: Tuple[float,float],
                 item_process_time: float = ITEM_PROCESS_TIME, pallet_unload_time: float = BUFFER_PROCESS_TIME):
        super().__init__(env, depalletizer_id)
        self.process = env.process(self._run())
        self._coordinate = coordinate
        self._item_process_time = item_process_time
        self._pallet_unload_time = pallet_unload_time
        self._payload: Optional[SystemPallet] = None
        self._current_item_id: Optional[int] = None
        self._remaining_qty: Optional[int] = None
        self._on_load_event = None

    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> Tuple[float, float]:
        return self._coordinate

    @property
    def payload(self) -> SystemPallet:
        return self._payload

    @property
    def current_item_id(self) -> int:
        return self._current_item_id

    @property
    def remaining_qty(self) -> int:
        return self._remaining_qty

    # --------
    #  Logic
    # --------

    def current_process_time_left(self) -> float:
        """Calculate the expected time to left process the current order."""
        if self._payload is None:
            return 0.0

        item_time = self._remaining_qty * self._item_process_time
        total_time = item_time + self._pallet_unload_time
        return total_time

    def can_load(self) -> bool:
        return self._payload is None

    def load(self, pallet: SystemPallet):
        """Update pallet on depalletizer."""
        if self.can_load():
            self._payload = pallet
            pallet.actual_location.update(coordinates=self.coordinate, element_name=f"{self}")
            print(f"[{self.env.now}] {self}: Loaded {pallet}")

            # Get items to process
            order = self._payload.order
            if isinstance(order, RefillOrder):
                self._current_item_id = order.item_id
                self._remaining_qty = order.qty

            # Fire processing event if depalletizer is waiting
            if self._on_load_event and not self._on_load_event.triggered:
                self._on_load_event.succeed(self)

    def _handoff_pallet(self):
        """Pass pallet downstream after items have been unloaded."""
        if self._output and self._payload is not None:
            yield self.env.timeout(self._pallet_unload_time)
            print(f"[{self.env.now}] {self}: Unloaded {self._payload}")
            self._output.load(self._payload)  # Pass to downstream
            self._payload = None


    def _process_item(self):
        """Load item into item conveyor infeed"""
        yield self.env.timeout(self._item_process_time)
        # TODO load item on conveyor


    def _run(self):
        """Main depalletizing loop."""
        while True:
            self._on_load_event = self.env.event()
            yield self._on_load_event  # wait for pallet
            print(f"[{self.env.now}] {self}: Started depalletizing {self._payload.order}")
            self._on_load_event = None

            # Process items
            while self._remaining_qty > 0:
                yield self.env.process(self._process_item())
                self._remaining_qty -= 1
            self._current_item_id = None

            # TODO handoff ItemBatch if ready_event not yet triggered

            # Unload empty pallet
            self._payload.order.status = OrderStatus.COMPLETED  # Update order status
            print(f"[{self.env.now}] {self}: Depalletized {self._payload.order}")
            self._payload.clear_order()  # Clear pallet status
            yield self.env.process(self._handoff_pallet())
