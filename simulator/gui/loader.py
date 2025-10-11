from simulator.gui.component_items import (BaseItem, PayloadBufferItem,
                                           PayloadConveyorItem, PalletItem, DepalletizerItem, BatchBuilderItem)
from simulator.core.components.component import Component
from simulator.core.transportation_units.system_pallet import SystemPallet

# Registry for gui components
COMPONENT_ITEM_TYPES = {
    "PayloadConveyor" : PayloadConveyorItem,
    "PayloadBuffer" : PayloadBufferItem,
    "Depalletizer" : DepalletizerItem,
    "BatchBuilder" : BatchBuilderItem
}

def load_component_items(component_items: dict[str, "BaseItem"],
                         components: dict[str,"Component"],
                         pallets: dict[int, "SystemPallet"]):
    """
    Create gui component items from simulator components and pallets.
    """
    # Create components
    for component in components.values():
        comp_type = component.type

        # Ensure the component has a valid type
        if comp_type not in COMPONENT_ITEM_TYPES:
            raise ValueError(f"Unknown component type: {comp_type}")

        cls = COMPONENT_ITEM_TYPES[comp_type]

        # Create component item based on attributes
        if hasattr(component, "start") and hasattr(component, "end"):
            component_item = cls(start=component.start, end=component.end)
        elif hasattr(component, "coordinate"):
            component_item = cls(coordinate=component.coordinate)
        else:
            raise ValueError(f"Cannot model component: {component.id}")

        # Create dict entry
        component_items[component.id] = component_item

    # Create pallets
    for pallet_id in pallets.keys():
        component_items[str(pallet_id)] = PalletItem()