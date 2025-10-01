import math
from simulator.core.orders.order import RefillOrder, OpmOrder
from simulator.core.stock.warehouse import Warehouse
from simulator.core.items.catalogue import Catalogue
from simulator.core.factory.id_gen import IDGenerator
from simulator.config import EURO_PALLET_MAX_WEIGHT, EURO_PALLET_MAX_VOLUME
import simpy

class InventoryManager:
    """
    Interface for placing orders in the material flow system.
    Handles manual order placing from Warehouse->ItemWarehouse (RefillOrder) and ItemWarehouse->OPM (OpmOrder).
    Also supports automatic demand driven RefillOrder generating/dispatching if being subscribed to.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    process : simpy.Process
        SimPy process instance for this component.
    catalogue : Catalogue
        Helper methods for order-related calculations
    warehouse : Warehouse
        Stores instance of warehouse for order placing.
    itemwarehouse : ItemWarehouse

    auto_refill_event : simpy.events.Event
        Event to trigger automatic RefillOrders
    """
    def __init__(self, env: simpy.Environment, id_gen: IDGenerator, catalogue: Catalogue, warehouse: Warehouse):
        self.env = env
        # self.process = env.process(self.run())
        self._id_gen = id_gen
        self._catalogue = catalogue
        self._warehouse = warehouse
        self._auto_refill_event = None

    # ---------------
    # Public methods
    # ---------------

    def place_refill_order(self, item_id: int, qty_requested: int):
        """Place refill order(s) to warehouse queue."""
        # Calculate how many pallets are needed for order
        # Determined by max qty per pallet
        qty_per_pallet = self._catalogue.qty_per_pallet(item_id, EURO_PALLET_MAX_VOLUME, EURO_PALLET_MAX_WEIGHT)
        pallets_consumed = math.ceil(qty_requested / qty_per_pallet)

        # Generate orders
        for _ in range(pallets_consumed):
            order_id = self._id_gen.generate_id(type_digit=5, length=6)
            new_order = RefillOrder(order_id, item_id, qty_per_pallet)
            self._warehouse.place_order(order=new_order, priority=10)

    # TODO:
    # Implement order priority calculation

    # TODO:
    # Implement automatic RefillOrder generating