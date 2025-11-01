from simulator.core.orders.order import RefillOrder, OpmOrder
from simulator.core.stock.warehouse import Warehouse
from simulator.core.stock.item_warehouse import ItemWarehouse
from simulator.core.items.catalogue import Catalogue
from simulator.core.utils.id_gen import IDGenerator
from simulator.config import EURO_PALLET_MAX_WEIGHT, EURO_PALLET_MAX_VOLUME, REQUESTED_ITEM_SCAN_INTERVAL
import simpy

class InventoryManager:
    """
    Interface for placing orders in the material flow system.
    Handles manual order placing from Warehouse->ItemWarehouse (RefillOrder)
    and ItemWarehouse->OPM (OpmOrder).

    Attributes
    ----------
    env : simpy.Environment
        The simulation environment
    catalogue : Catalogue
        Helper methods for order-related calculations
    warehouse : Warehouse
        Stores instance of warehouse for order placing.
    item_warehouse : ItemWarehouse
        Stores instance of item warehouse for order placing.
    process_auto_refill : simpy.Process
        SimPy process instance for auto refill loop
    refill_scan_interval : float
        Time in simulation units for auto refill order scan interval
    """
    def __init__(self, env: simpy.Environment,
                 id_gen: IDGenerator,
                 catalogue: Catalogue,
                 warehouse: Warehouse,
                 item_warehouse: ItemWarehouse,
                 refill_scan_interval = REQUESTED_ITEM_SCAN_INTERVAL):
        self.env = env
        self._id_gen = id_gen
        self._catalogue = catalogue
        self._warehouse = warehouse
        self._item_warehouse = item_warehouse
        self.process_auto_refill = self.env.process(self._listen_for_requested_items())
        self._refill_scan_interval = refill_scan_interval

    # ---------------
    # Private helpers
    # ---------------

    def _sim_time(self) -> float:
        """Get current sim time with 1 decimal precision."""
        return round(self.env.now, 1)

    # ---------------
    # Public methods
    # ---------------

    def place_refill_order(self, item_id: int, qty_requested: int):
        """Place refill order(s) to warehouse queue."""
        # Calculate how many pallets are needed for order
        # Determined by max qty per pallet
        max_qty_per_pallet = self._catalogue.qty_per_pallet(item_id, EURO_PALLET_MAX_VOLUME, EURO_PALLET_MAX_WEIGHT)

        # Get full pallets and leftover qty
        full_pallets_consumed = qty_requested // max_qty_per_pallet
        leftover_qty = qty_requested - (full_pallets_consumed * max_qty_per_pallet)

        # Get the order timestamp
        order_time = self._sim_time()

        # Generate full orders
        for _ in range(full_pallets_consumed):
            order_id = self._id_gen.generate_id(type_digit=5, length=6)
            new_order = RefillOrder(order_id, order_time, item_id, max_qty_per_pallet)
            self._warehouse.place_order(order=new_order, priority=order_time)

        # Generate the last order from leftover qty
        order_id = self._id_gen.generate_id(type_digit=5, length=6)
        new_order = RefillOrder(order_id, order_time, item_id, leftover_qty)
        self._warehouse.place_order(order=new_order, priority=order_time)

    def place_opm_order(self, items: dict[int,int]):
        """Place opm order to item warehouse queue."""
        # Generate the order instance
        order_time = self._sim_time()
        order_id = self._id_gen.generate_id(type_digit=6, length=6)
        new_order = OpmOrder(order_id, order_time, items)
        self._item_warehouse.place_order(new_order, priority=order_time)

    def _listen_for_requested_items(self):
        """Listen for requested items in item warehouse."""
        while True:
            yield self.env.timeout(self._refill_scan_interval) # Simulate a scanning interval

            if len(self._item_warehouse.requested_items_queue.items) == 0:
                continue

            # Scan the whole request queue for items and their quantities
            requested_items: dict[int,int] = {}
            while len(self._item_warehouse.requested_items_queue.items) > 0:
                request = yield self._item_warehouse.requested_items_queue.get()
                item_id = request.get('item_id')
                qty = request.get('qty')

                if item_id is not None and qty is not None:
                    # Add the requested quantity to the existing total for that item
                    requested_items[item_id] = requested_items.get(item_id, 0) + qty

            # Place the needed refill orders
            for item_id, qty in requested_items.items():
                self.place_refill_order(item_id, qty)