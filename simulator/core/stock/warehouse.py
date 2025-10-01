import simpy
from simulator.core.orders.order import RefillOrder, OrderStatus
from simulator.core.stock.stock import Stock
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.transportation_units.transportation_unit import Location
from simulator.config import ORDER_MERGE_TIME, WAREHOUSE_MAX_PALLET_CAPACITY, PALLET_BUFFER_PROCESS_TIME

class Warehouse(Stock):
    """
    Manages item refills to ItemWarehouse (RefillOrder).
    Contains an I/O component (PayloadBuffer) where orders get merged on pallets.
    Also stores system pallets.

    Additional Attributes
    ----------
    input_buffer : PayloadBuffer
        Infeed for empty pallets
    output_buffer : PayloadBuffer
        I/O component where orders get merged on pallets.
    order_process_time : float
        Time to process an order.
    pallet_process_time : float
        Time to process a pallet.
    pallet_store : simpy.Store
        Store of empty pallets
    pallet_capacity : int
        Max amount of pallets the warehouse can store.
    """
    def __init__(self, env: simpy.Environment,
                 order_process_time: float = ORDER_MERGE_TIME,
                 pallet_process_time: float = PALLET_BUFFER_PROCESS_TIME,
                 pallet_capacity: int = WAREHOUSE_MAX_PALLET_CAPACITY):
        super().__init__(env=env)
        self._input_buffer: PayloadBuffer | None = None
        self._output_buffer : PayloadBuffer | None = None
        self._order_process_time = order_process_time
        self._pallet_process_time = pallet_process_time
        self._pallet_store = simpy.Store(self.env, pallet_capacity)
        self._pallet_capacity = pallet_capacity

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

    # -----------------
    # Buffer injection
    # -----------------

    @input_buffer.setter
    def input_buffer(self, buffer):
        """Dependency inject a buffer for the warehouse."""
        if not isinstance(buffer, PayloadBuffer):
            raise ValueError("buffer must be PayloadBuffer object")
        self._input_buffer = buffer
        self.env.process(self._listen_for_pallets())

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
        return new_pallet

    def process_order(self, order: RefillOrder):
        """Process order by merging it on the pallet on buffer."""
        # After processing pallet is routed to depalletizers
        pallet = self._output_buffer.payload
        if isinstance(pallet, SystemPallet):
            pallet.merge_order(new_order=order, destination_type="depalletizer")
            order.status = OrderStatus.IN_PROGRESS # Update order status to pending
            yield self.env.timeout(self._order_process_time)
            print(f"[{self.env.now}] Warehouse: Processed order {order}")

    def _listen_for_pallets(self):
        """Continuously listen for pallets arriving in the input buffer."""
        while True:
            self._input_buffer.on_load_event = self.env.event()
            pallet = yield self._input_buffer.on_load_event  # wait for pallet

            if pallet is None:
                # Wait until a pallet exists
                yield self.env.timeout(0)
                continue

            yield self.env.timeout(self._pallet_process_time) # Pallet processing delay
            yield self._pallet_store.put(pallet)
            self._input_buffer.clear() # Clear pallet from buffer

            print(f"[{self.env.now}] Warehouse: Stored empty pallet {pallet}")

    def _run(self):
        """Main order processing loop"""
        while True:
            # Wait until a pallet is available in warehouse
            pallet = yield self._pallet_store.get()
            print(f"[{self.env.now}] {self}: Took pallet {pallet} from pallet store")

            # Load pallet into buffer
            self._output_buffer.load(pallet)
            print(f"[{self.env.now}] {self}: Loaded {pallet} into buffer")

            # Process orders if available
            if self._has_orders():
                order = self._next_order()
                print(f"[{self.env.now}] {self}: Processing order {order}")

                # run the order process
                yield self.env.process(self.process_order(order))

                # trigger buffer handoff
                yield self.env.process(self._output_buffer.handoff())
            else:
                print(f"[{self.env.now}] {self}: No orders in queue!")