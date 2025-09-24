from simulator.core.components.component import Component
from simulator.core.stock.warehouse import Warehouse
from simulator.core.orders.inventory_manager import InventoryManager
from simulator.core.transportation_units.transportation_unit import TransportationUnit
from typing import List, Optional
from simulator.core.factory.loader import *

class Factory:
    """
    The orchestration layer for the factory simulator.
    Stores all base object instances and has API-functions to access factory-data.

    Attributes
    ----------
    components : dict[int,Component]
        All physical components of the factory keyed by id
    warehouse : Warehouse
        To access main warehouse
    itemwarehouse : ItemWarehouse
        To access item warehouse
    inventory_manager : InventoryManager
        For managing the factory inventory (stock and orders)
    transportation_units : dict[int,TransportationUnit]
        All transportation units available keyed by id
    db : DatabaseManager
        Access the database
    factory_graph : FactoryGraph
        Access the factory layout
    """
    def __init__(self):
        self._components: dict[int,Component] = {}
        self._warehouse: Optional[Warehouse] = None
        #self._itemwarehouse: Optional[ItemWarehouse] = None
        self._inventory_manager: Optional[InventoryManager] = None
        self._transportation_units: dict[int,TransportationUnit] = {}
        #self._database: Optional[DatabaseManager] = None
        # self._factory_graph: Optional[FactoryGraph] = None

    # ----------------
    # Private helpers
    # ----------------

    def _load_components(self, json_name: str) -> dict[int, Component]:
        project_root = Path(__file__).parent.parent.parent.parent
        json_path = project_root / "data" / json_name
        return load_components_from_json(str(json_path))

    # --------------
    # Public methods
    # --------------

    def get_component(self, component_id: int) -> Optional[Component]:
        if component_id not in self._components:
            return None
        return self._components[component_id]