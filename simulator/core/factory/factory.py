import simpy
from simulator.core.components.component import Component
from simulator.core.stock.warehouse import Warehouse
from simulator.core.stock.item_warehouse import ItemWarehouse
from simulator.core.orders.inventory_manager import InventoryManager
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.factory.loader import load_factory_from_json
from simulator.core.items.catalogue import Catalogue
from pathlib import Path
from simulator.config import ITEM_JSON, FACTORY_JSON, WAREHOUSE_MAX_PALLET_CAPACITY
from simulator.core.utils.event_bus import EventBus
from simulator.core.utils.id_gen_config import id_generator

class Factory:
    """
    The orchestration layer for the factory simulator.
    Stores all base object instances and has API-functions to access factory-data.

    Attributes
    ----------
    env : simpy.Environment
        The simulation environment
    components : dict[str,Component]
        All physical components of the factory keyed by id
    warehouse : Warehouse
        To access main warehouse
    item_warehouse : ItemWarehouse
        To access item warehouse
    catalogue : Catalogue
        Store warehouse item catalogue.
    inventory_manager : InventoryManager
        For managing the factory inventory (stock and orders)
    pallets : dict[int,SystemPallet]
        All SystemPallets available keyed by id
    event_bus : EventBus
        Stateless service for passing events to gui and database.
        Allows communication with GUI and database
    """
    def __init__(self, env: simpy.Environment,
                 event_bus: EventBus | None = None,
                 items_json_name: str = ITEM_JSON,
                 layout_json_name: str = FACTORY_JSON):
        self.env = env
        self.components: dict[str,Component] = {}
        self.warehouse = Warehouse(env)
        self.item_warehouse = ItemWarehouse(env)
        self.catalogue = Catalogue(items_json_name)
        self.inventory_manager = InventoryManager(env=env,
                                                  catalogue=self.catalogue,
                                                  warehouse=self.warehouse,
                                                  item_warehouse=self.item_warehouse)
        self.pallets: dict[int,SystemPallet] = {}
        self.event_bus = event_bus

        # Load layout from json
        self._load_factory(layout_json_name)


    # ----------------
    # Private helpers
    # ----------------

    def _load_factory(self, json_name: str) -> dict[str, Component]:
        project_root = Path(__file__).parent.parent.parent.parent
        json_path = project_root / "data" / json_name
        return load_factory_from_json(file_path=str(json_path),
                                      env=self.env,
                                      components=self.components,
                                      warehouse=self.warehouse,
                                      item_warehouse=self.item_warehouse)

    def _init_pallets(self, pallet_qty: int):
        """Initialize given amount of pallets and store to warehouse."""
        # Make sure doesn't exceed warehouse pallet capacity
        pallet_qty = min(pallet_qty, self.warehouse.pallet_capacity)

        for _ in range(pallet_qty):
            pallet_id = id_generator.generate_id(1, 8) # SystemPallet ids are 8 digits starting with 1
            pallet = self.warehouse.create_pallet(pallet_id)
            self.pallets[pallet_id] = pallet

    def _inject_eventbus(self, bus: EventBus):
        """Pass event bus to every object that interacts with gui"""
        for component in self.components.values():
            component.inject_event_bus(bus)

        for pallet in self.pallets.values():
            pallet.event_bus = bus

        self.warehouse.inject_eventbus(bus)
        self.item_warehouse.inject_eventbus(bus)

    def _emit_catalogue_items(self):
        """Emit all items in catalogue through event bus for database setup."""
        for item_id, item in self.catalogue.items:
            self.event_bus.emit("create_item", {
                "item_id": item_id,
                "name": item.name,
                "weight": item.weight,
                "category": item.category,
                "volume": item.volume,
                "stackable": item.stackable
            })

    # --------------
    # Public methods
    # --------------

    def get_component(self, component_id: str) -> Component | None:
        if component_id not in self.components:
            return None
        return self.components[component_id]

    def init_simulation(self):
        """
        Initialize simulation.
        Stores requested amount of pallets in warehouse,
        fills ItemWarehouse with initial stock,
        places initial orders.
        """
        self._inject_eventbus(self.event_bus)
        self._init_pallets(WAREHOUSE_MAX_PALLET_CAPACITY)
        self._emit_catalogue_items()
