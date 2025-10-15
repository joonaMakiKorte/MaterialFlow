from simulator.gui.component_items import (BaseComponentItem, PayloadBufferItem,
                                           PayloadConveyorItem, DepalletizerItem, BatchBuilderItem,
                                           WarehouseItem)
from simulator.core.stock.warehouse import Warehouse
from simulator.core.factory.factory import Factory

# Registry for gui components
COMPONENT_ITEM_TYPES = {
    "PayloadConveyor" : PayloadConveyorItem,
    "PayloadBuffer" : PayloadBufferItem,
    "Depalletizer" : DepalletizerItem,
    "BatchBuilder" : BatchBuilderItem
}

def load_items(component_items: dict[str, "BaseComponentItem"],
                         factory: Factory, event_bus):
    """
    Create gui component items from simulator components and pallets.
    """
    # Create components
    for component in factory.components.values():
        comp_type = component.type

        # Ensure the component has a valid type
        if comp_type not in COMPONENT_ITEM_TYPES:
            raise ValueError(f"Unknown component type: {comp_type}")

        cls = COMPONENT_ITEM_TYPES[comp_type]

        # Create component item based on attributes
        if hasattr(component, "start") and hasattr(component, "end"):
            component_item = cls(component.id, start=component.start, end=component.end, event_bus=event_bus)
        elif hasattr(component, "coordinate"):
            component_item = cls(component.id, coordinate=component.coordinate, event_bus=event_bus)
        else:
            raise ValueError(f"Cannot model component: {component.id}")

        # Create dict entry
        component_items[component.id] = component_item

    # Create warehouse
    warehouse = factory.warehouse
    warehouse_item = WarehouseItem(input_buffer_pos=warehouse.input_buffer.coordinate,
                                   output_buffer_pos=warehouse.output_buffer.coordinate,
                                   event_bus=event_bus)
    # Create dict entry with 'warehouse'-key
    component_items["warehouse"] = warehouse_item