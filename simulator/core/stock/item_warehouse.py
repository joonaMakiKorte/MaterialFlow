import simpy
import heapq
import math
from simulator.core.orders.order import OpmOrder
from simulator.core.stock.stock import Stock
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.transportation_units.item_batch import ItemBatch
from simulator.config import ITEM_PROCESS_TIME, ITEM_WAREHOUSE_MAX_ITEM_CAPACITY, BATCH_BUFFER_PROCESS_TIME
from simulator.gui.event_bus import EventBus


class ItemWarehouse(Stock):
    """
    Manages storage and distribution of individual items.
    Can contain multiple input buffers and output batch builders.
    Input item flow comes as batches from buffers,
    output item flow builds batches upon batch builders.

    Additional Attributes
    ---------------------
    process_listeners : list[simpy.Process]
        SimPy process instances of batch inputs. Corresponding input buffer is found by idx
        in input_buffers.
    input_buffers : list[PayloadBuffer]
        List of available input buffers
    output_buffers : list[BatchBuffer]
        List of available output buffers
    item_stock : dict[int,int]
        Different item quantities in stock keyed by item id
    item_capacity : int
        Max capacity of items the warehouse can store
    item_count : int
        Current count of items in the stock
    item_process_time : float
        Time in simulation units it takes to unload one item
    batch_process_time : float
        Time in simulation units it takes to process (load) one batch
    """
    def __init__(self, env: simpy.Environment,
                 item_process_time: float = ITEM_PROCESS_TIME,
                 batch_process_time: float = BATCH_BUFFER_PROCESS_TIME,
                 item_capacity: int = ITEM_WAREHOUSE_MAX_ITEM_CAPACITY):
        super().__init__(env=env)
        self.process_listeners = []
        self._input_buffers: list[PayloadBuffer] = []
        self._output_buffers: list[BatchBuilder] = []
        self._item_stock: dict[int, int] = {}
        self._item_capacity = item_capacity
        self._item_count: int = 0
        self._item_process_time = item_process_time
        self._batch_process_time = batch_process_time

    # ----------
    # Properties
    # ----------



    # ----------------
    # Buffer injection
    # ----------------

    def inject_input_buffer(self, buffer):
        """Dependency inject a buffer."""
        if not isinstance(buffer, PayloadBuffer):
            raise ValueError("buffer must be PayloadBuffer object")
        self._input_buffers.append(buffer)
        self.process_listeners.append(self.env.process(self._listen_for_batch(buffer)))

    def inject_output_buffer(self, buffer):
        if not isinstance(buffer, BatchBuilder):
            raise ValueError("buffer must be BatchBuilder object")
        self._output_buffers.append(buffer)


    # --------
    #  Logic
    # --------

    def place_order(self, order: OpmOrder, priority: int):
        """Insert an order with given priority (lower = higher priority)."""
        count = next(self._counter)  # Prevents comparasion errors when priorities match
        heapq.heappush(self._order_queue, (priority, count, order))
        if self.event_bus is not None:
            self.event_bus.emit("itemwarehouse_order_count", {"count": len(self._order_queue)})

    def process_order(self, order: OpmOrder):
        pass

    def inject_eventbus(self, event_bus: EventBus):
        self.event_bus = event_bus
        # Emit item and order count
        fill_percentage = math.ceil(self._item_count / self._item_capacity) * 100
        self.event_bus.emit("warehouse_item_count",
                            {"count": self._item_count, "available":fill_percentage})
        self.event_bus.emit("warehouse_order_count", {"count": len(self._order_queue)})

    def _load_batch(self, batch: ItemBatch):
        """Load items from batch into storage."""
        batch_item_count = batch.item_count

        # Wait until there is room for the batch items
        while self._item_count + batch_item_count > self._item_capacity:
            yield self.env.timeout(0.5)
            continue
        self._item_count += batch_item_count

        # Load items
        items = batch.items
        for item, qty in items.items():
            if not self._item_stock.get(item):
                # Check if we need to create new entry in stock
                self._item_stock[item] = 0
            self._item_stock[item] += qty

        yield self.env.timeout(self._batch_process_time)


    def _listen_for_batch(self, buffer: PayloadBuffer):
        """Continuously listen for batches arriving in input buffer."""
        while True:
            buffer.on_load_event = self.env.event()
            batch = yield buffer.on_load_event

            if batch is None:
                # Wait until a batch exists
                yield self.env.timeout(0.5)
                continue

            yield self.env.process(self._load_batch(batch))
            buffer.clear() # Clear pallet from buffer
            print(f"[{self.env.now}] ItemWarehouse: Stored batch {batch}")

    def _order_loop(self):
        while True:
            yield self.env.timeout(100)
