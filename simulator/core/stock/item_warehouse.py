import simpy
import heapq
import math
from simulator.core.orders.order import OpmOrder
from simulator.core.stock.stock import Stock
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.transportation_units.item_batch import ItemBatch
from simulator.config import ITEM_PROCESS_TIME, ITEM_WAREHOUSE_MAX_ITEM_CAPACITY, BATCH_BUFFER_PROCESS_TIME
from simulator.core.utils.event_bus import EventBus
from simulator.core.utils.logging_config import log_manager


class ItemWarehouse(Stock):
    """
    Manages storage and distribution of individual items.
    Can contain multiple input buffers and output batch builders.
    Input item flow comes as batches from buffers,
    output item flow builds batches upon batch builders.

    Additional Attributes
    ---------------------
    process_order_processes : simpy.Process
        SimPy process instance for processing orders that have sufficient stock
    process_input_listeners : list[simpy.Process]
        SimPy process instances of batch inputs. Corresponding input buffer is found by idx
        in input_buffers.
    process_output_listeners : list[simpy.Process]
        SimPy process instances of batch outputs (order processing). Corresponding output buffer is found by idx
        in output_buffers.
    order_events : dict[str, simpy.events.Event]
        Order events for buffers keyed by buffer id.
    processable_order_queue : min-heap
        Queue for orders that can be processed (there is enough stock available)
    stock_requested_orders : set
        Track orders for which stock has already been requested
    input_buffers : list[PayloadBuffer]
        List of available input buffers
    output_buffers : list[BatchBuffer]
        List of available output buffers
    item_stock : dict[int,int]
        Different item quantities in stock keyed by item id
    available_item_stock : dict[int, int]
        Contains the items from item_stock that are not locked by order yet, meaning those are available
    item_capacity : int
        Max capacity of items the warehouse can store
    item_count : int
        Current count of items in the stock
    item_process_time : float
        Time in simulation units it takes to unload one item
    batch_process_time : float
        Time in simulation units it takes to process (load) one batch
    requested_items_queue : simpy.Store
        A queue for external managers to know which items are needed
    """
    def __init__(self, env: simpy.Environment,
                 item_process_time: float = ITEM_PROCESS_TIME,
                 batch_process_time: float = BATCH_BUFFER_PROCESS_TIME,
                 item_capacity: int = ITEM_WAREHOUSE_MAX_ITEM_CAPACITY):
        super().__init__(env=env)
        self.process_input_listeners = []
        self.process_output_listeners = []
        self.order_events = {}
        self._processable_order_queue = []
        self._stock_requested_orders = set()
        self._input_buffers: list[PayloadBuffer] = []
        self._output_buffers: list[BatchBuilder] = []
        self._item_stock: dict[int, int] = {}
        self._available_item_stock: dict[int, int] = {}
        self._item_capacity = item_capacity
        self._item_count: int = 0
        self._item_process_time = item_process_time
        self._batch_process_time = batch_process_time
        self.requested_items_queue = simpy.Store(env)

    # ----------
    # Properties
    # ----------

    @property
    def input_buffers(self) -> list[PayloadBuffer]:
        return self._input_buffers

    @property
    def output_buffers(self) -> list[BatchBuilder]:
        return self._output_buffers

    # ----------------
    # Buffer injection
    # ----------------

    def inject_input_buffer(self, buffer):
        """Dependency inject a buffer."""
        if not isinstance(buffer, PayloadBuffer):
            raise ValueError("buffer must be PayloadBuffer object")
        self._input_buffers.append(buffer)
        self.process_input_listeners.append(self.env.process(self._listen_for_batch(buffer)))

    def inject_output_buffer(self, buffer):
        if not isinstance(buffer, BatchBuilder):
            raise ValueError("buffer must be BatchBuilder object")
        self._output_buffers.append(buffer)
        self.order_events[buffer.id] = None # Indicate buffer is free for orders
        self.process_output_listeners.append(self.env.process(self._listen_for_order(buffer)))

    # ---------------
    # Private helpers
    # ---------------

    def _get_available_buffer_id(self) -> str | None:
        """Gets the ID of an available output buffer."""
        for buffer_id, event in self.order_events.items():
            if event is None:
                return buffer_id
        return None

    def _has_sufficient_stock(self, order: OpmOrder) -> bool:
        """Checks if there is enough stock to fulfill the given order."""
        for item_id, requested_qty in order.items.items():
            if self._available_item_stock.get(item_id, 0) < requested_qty:
                return False
        return True

    def _request_missing_items(self, order: OpmOrder):
        """Puts a request for missing items for an order into the request queue."""
        for item_id, requested_qty in order.items.items():
            stock_qty = self._item_stock.get(item_id, 0)
            if stock_qty < requested_qty:
                missing_qty = requested_qty - stock_qty
                request = {'item_id': item_id, 'qty': missing_qty}
                self.requested_items_queue.put(request)
                log_manager.log(f"Item {item_id} out of stock: requested {missing_qty} more",
                                component_id=self.__class__.__name__,
                                sim_time=self.env.now)

    def _reserve_stock(self, items: dict[int, int]):
        """Reserve items for an order by removing them from available items dict"""
        for item_id, qty in items.items():
            self._available_item_stock[item_id] -= qty

    # --------
    #  Logic
    # --------

    def place_order(self, order: OpmOrder, priority: float):
        """Insert an order with given priority (lower = higher priority)."""
        count = next(self._counter)  # Prevents comparasion errors when priorities match
        heapq.heappush(self._order_queue, (priority, count, order))
        if self.event_bus is not None:
            self.event_bus.emit("item_warehouse_order_count", {"count": len(self._order_queue)})

    def process_order(self, order: OpmOrder, buffer: BatchBuilder):
        """Process an order by taking items from stock and simulating the picking time."""
        log_manager.log(f"Processing order {order.id} for buffer {buffer.id}",
                        component_id=self.__class__.__name__,
                        sim_time=self.env.now)

        # Decrement stock for each item in the order
        for item_id, qty in order.items.items():
            self._item_stock[item_id] -= qty
            self._item_count -= qty

        # Simulate picking and processing time
        processing_time = len(order.items) * self._item_process_time
        yield self.env.timeout(processing_time)

        log_manager.log(f"Finished processing order {order.id}",
                        component_id=self.__class__.__name__,
                        sim_time=self.env.now)

        if self.event_bus is not None:
            fill_percentage = math.ceil(self._item_count / self._item_capacity) * 100
            self.event_bus.emit("item_warehouse_item_count",
                                {"count": self._item_count, "fill": fill_percentage})
            self.event_bus.emit("item_warehouse_order_count", {"count": len(self._order_queue)})

    def inject_eventbus(self, event_bus: EventBus):
        self.event_bus = event_bus
        # Emit item and order count
        fill_percentage = math.ceil(self._item_count / self._item_capacity) * 100
        self.event_bus.emit("item_warehouse_item_count",
                            {"count": self._item_count, "fill":fill_percentage})
        self.event_bus.emit("item_warehouse_order_count", {"count": len(self._order_queue)})

    def _load_batch(self, batch: ItemBatch):
        """Load items from batch into storage."""
        batch_item_count = batch.item_count
        # Wait until there is room for the batch items
        while self._item_count + batch_item_count > self._item_capacity:
            yield self.env.timeout(0.5)
        self._item_count += batch_item_count

        # Load items
        items = batch.items
        for item, qty in items.items():
            self._item_stock.setdefault(item, 0)
            self._available_item_stock.setdefault(item, 0)
            self._item_stock[item] += qty
            self._available_item_stock[item] += qty
        yield self.env.timeout(self._batch_process_time)

        if self.event_bus is not None:
            fill_percentage = math.ceil(self._item_count / self._item_capacity) * 100
            self.event_bus.emit("item_warehouse_item_count",
                                {"count": self._item_count, "fill":fill_percentage})

    def _listen_for_batch(self, buffer: PayloadBuffer):
        """Continuously listen for batches arriving in input buffer."""
        while True:
            buffer.on_load_event = self.env.event()
            batch = yield buffer.on_load_event
            yield self.env.process(self._load_batch(batch))
            buffer.clear() # Clear pallet from buffer
            
            if self.event_bus is not None:
                self.event_bus.emit("store_payload", {"id":batch.id})
            log_manager.log(f"Stored batch {batch}",
                        component_id=self.__class__.__name__,
                        sim_time=self.env.now)

    def _listen_for_order(self, buffer: BatchBuilder):
        """Listens for orders assigned for the specific buffer."""
        buffer_id = buffer.id
        while True:
            order_event = self.env.event()
            self.order_events[buffer_id] = order_event
            order = yield order_event

            if order:
                yield self.env.process(self.process_order(order, buffer))

            # Mark the buffer as available again
            self.order_events[buffer_id] = None

    def _order_loop(self):
        """Continuously monitor requested orders and check the requested item availability."""
        while True:
            # Wait until there is at least one order in the main queue
            if not self._has_orders():
                 yield self.env.timeout(0.5)
                 continue

            # Use a temporary list to hold orders that are not ready yet
            pending_orders = []

            while self._has_orders():
                priority, count, order = heapq.heappop(self._order_queue)
                if self._has_sufficient_stock(order):
                    # If order can be fulfilled, add to processable queue and reserve needed stock
                    heapq.heappush(self._processable_order_queue, (priority, count, order))
                    self._stock_requested_orders.discard(order.id)
                    if isinstance(order, OpmOrder):
                        self._reserve_stock(order.items)
                else:
                    pending_orders.append((priority, count, order))

                    # Request items for order if haven't done so yet
                    if order.id not in self._stock_requested_orders:
                        self._request_missing_items(order)
                        self._stock_requested_orders.add(order.id)

            # Re-add pending orders back into the main priority queue
            for entry in pending_orders:
                heapq.heappush(self._order_queue, entry)

            yield self.env.timeout(1)
