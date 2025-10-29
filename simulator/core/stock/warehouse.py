import simpy
import heapq
import math
from simulator.core.orders.order import RefillOrder, OrderStatus, Order
from simulator.core.stock.stock import Stock
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.transportation_units.transportation_unit import Location
from simulator.config import ORDER_MERGE_TIME, WAREHOUSE_MAX_PALLET_CAPACITY, PALLET_BUFFER_PROCESS_TIME
from simulator.gui.component_items import PALLET_ORDER_STATES
from simulator.gui.event_bus import EventBus
from simulator.core.factory.log_manager import log_context


class Warehouse(Stock):
    """
    Manages item refills to ItemWarehouse (RefillOrder).
    Contains I/O components (PayloadBuffer) for pallet input and output.
    Orders get merged on pallets on output buffer.
    Also stores system pallets.

    Additional Attributes
    ----------
    process_listener : simpy.Process
        SimPy process instance for listening pallet input.
    input_buffer : PayloadBuffer
        Infeed for empty pallets
    output_buffer : PayloadBuffer
        I/O component where orders get merged on pallets.
    order_process_time : float
        Time to process an order.
    pallet_process_time : float
        Time to process a pallet.
    pallet_store : simpy.Store
        Store of empty pallets (FIFO queue)
    pallet_capacity : int
        Max amount of pallets the warehouse can store.
    pallet_count : int
        Track the amount of pallets stored
    """
    def __init__(self, env: simpy.Environment,
                 order_process_time: float = ORDER_MERGE_TIME,
                 pallet_process_time: float = PALLET_BUFFER_PROCESS_TIME,
                 pallet_capacity: int = WAREHOUSE_MAX_PALLET_CAPACITY):
        super().__init__(env=env, name=self.__class__.__name__)
        self.process_listener = env.process(self._listen_for_pallets()) # Attach pallet listening process
        self._input_buffer: PayloadBuffer | None = None
        self._output_buffer : PayloadBuffer | None = None
        self._order_process_time = order_process_time
        self._pallet_process_time = pallet_process_time
        self._pallet_store = simpy.Store(env, pallet_capacity)
        self._pallet_capacity = pallet_capacity
        self._pallet_count = 0

    # ----------
    # Properties
    # ----------

    @property
    def input_buffer(self) -> PayloadBuffer:
        return self._input_buffer

    @property
    def output_buffer(self) -> PayloadBuffer:
        return self._output_buffer

    @property
    def order_process_time(self) -> float:
        return self._order_process_time

    @property
    def pallet_process_time(self) -> float:
        return self._pallet_process_time

    @property
    def pallet_capacity(self) -> int:
        return self._pallet_capacity

    @property
    def order_count(self) -> int:
        return len(self._order_queue)

    # -----------------
    # Buffer injection
    # -----------------

    @input_buffer.setter
    def input_buffer(self, buffer):
        """Dependency inject a buffer for the warehouse."""
        if not isinstance(buffer, PayloadBuffer):
            raise ValueError("buffer must be PayloadBuffer object")
        self._input_buffer = buffer

    @output_buffer.setter
    def output_buffer(self, buffer):
        """Dependency inject a buffer for the warehouse."""
        if not isinstance(buffer, PayloadBuffer):
            raise ValueError("buffer must be PayloadBuffer object")
        self._output_buffer = buffer

    # ----------
    #   Logic
    # ----------

    def create_pallet(self, pallet_id: int) -> SystemPallet:
        """Create a new pallet in warehouse. Return the pallet instance."""
        new_pallet = SystemPallet(pallet_id=pallet_id,
                                  actual_location=Location(element_name=self.__class__.__name__,
                                                           coordinates=self._output_buffer.coordinate))
        self._pallet_store.put(new_pallet)
        self._pallet_count += 1
        return new_pallet

    def place_order(self, order: RefillOrder, priority: float):
        """Insert an order with given priority (lower = higher priority)."""
        count = next(self._counter)  # Prevents comparasion errors when priorities match
        heapq.heappush(self._order_queue, (priority, count, order))
        if self.event_bus is not None:
            self.event_bus.emit("warehouse_order_count", {"count":len(self._order_queue)})

    def process_order(self, order: RefillOrder):
        """Process order by merging it on the pallet on buffer."""
        # After processing pallet is routed to depalletizers
        pallet = self._output_buffer.payload
        if isinstance(pallet, SystemPallet):
            self._logger.info(f"Processing order {order}", extra=log_context(self.env))
            yield self.env.timeout(self._order_process_time)
            pallet.merge_order(new_order=order, destination_type="depalletizer")
            self._logger.info(f"Merged order {order} on pallet {pallet}", extra=log_context(self.env))
            order.status = OrderStatus.IN_PROGRESS # Update order status to pending

            if self.event_bus is not None:
                self.event_bus.emit("update_payload_state",
                                    {"id": pallet.id, "state": PALLET_ORDER_STATES[order.type]})
                self.event_bus.emit("warehouse_order_count", {"count": len(self._order_queue)})

            self._logger.info(f"Processed order {order}", extra=log_context(self.env))

    def _listen_for_pallets(self):
        """Continuously listen for pallets arriving in the input buffer."""
        while True:
            self._input_buffer.on_load_event = self.env.event()
            pallet = yield self._input_buffer.on_load_event  # wait for pallet

            yield self.env.timeout(self._pallet_process_time) # Pallet processing delay
            yield self._pallet_store.put(pallet)
            self._pallet_count += 1
            self._input_buffer.clear() # Clear pallet from buffer

            if self.event_bus is not None:
                self.event_bus.emit("store_payload", {"id":pallet.id})
                fill_percentage = math.ceil(self._pallet_count / self._pallet_capacity) * 100
                self.event_bus.emit("warehouse_pallet_count",
                                    {"count": self._pallet_count, "fill": fill_percentage})

            self._logger.info(f"Stored empty pallet {pallet}", extra=log_context(self.env))

    def inject_eventbus(self, event_bus: EventBus):
        self.event_bus = event_bus
        # Emit order and pallet count
        fill_percentage = math.ceil(self._pallet_count/self._pallet_capacity) * 100
        self.event_bus.emit("warehouse_pallet_count",
                            {"count":self._pallet_count, "fill":fill_percentage})
        self.event_bus.emit("warehouse_order_count",{"count":len(self._order_queue)})

    def _order_loop(self):
        """Continuously monitor and process orders."""
        while True:
            # Wait until there's at least one order in the queue
            while not self._has_orders():
                # Check periodically for new orders
                yield self.env.timeout(0.5)

            # Wait until output buffer is ready to accept new pallet
            while not self._output_buffer.can_load():
                yield self.env.timeout(0.5)

            # Wait until a pallet becomes available in warehouse
            while len(self._pallet_store.items) == 0:
                # No pallets currently available — keep checking
                yield self.env.timeout(0.5)

            # Take a pallet from the store
            pallet: SystemPallet = yield self._pallet_store.get()
            self._logger.info(f"Took pallet {pallet} from storage", extra=log_context(self.env))

            # Simulate loading pallet into buffer
            yield self.env.timeout(PALLET_BUFFER_PROCESS_TIME)
            self._pallet_count -= 1

            # Process next available order
            order = self._next_order()

            if self.event_bus is not None:
                self.event_bus.emit("dispatch_pallet", {"id": pallet.id})
                pallets_available = math.ceil(
                    self._pallet_count / WAREHOUSE_MAX_PALLET_CAPACITY * 100)
                self.event_bus.emit("warehouse_pallet_count",
                                    {"count": self._pallet_count, "fill": pallets_available})
                self.event_bus.emit("warehouse_order_count", {"count": len(self._order_queue)})

            self._output_buffer.load(pallet)

            # Run order process
            yield self.env.process(self.process_order(order))

            # Trigger buffer handoff
            yield self.env.process(self._output_buffer.handoff())
