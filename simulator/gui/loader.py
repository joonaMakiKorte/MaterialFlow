from simulator.gui.component_items import (BaseComponentItem, PayloadBufferItem,
                                           PayloadConveyorItem, DepalletizerItem, BatchBuilderItem,
                                           WarehouseItem, ItemWarehouseItem)
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.factory.factory import Factory

# Registry for gui components
COMPONENT_ITEM_TYPES = {
    "PayloadConveyor" : PayloadConveyorItem,
    "PayloadBuffer" : PayloadBufferItem,
    "Junction" : PayloadBufferItem,
    "Depalletizer" : DepalletizerItem,
    "BatchBuilder" : BatchBuilderItem
}

def load_items(component_items: dict[str, "BaseComponentItem"],
                         factory: Factory, event_bus):
    """
    Create gui component items from simulator components and pallets.
    """
    # Create components
    components = factory.components.values()
    for component in components:
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

    # Create item warehouse
    item_warehouse = factory.item_warehouse
    # Get top-left and bottom right corners from buffer positions
    min_x, max_x, min_y, max_y = 99999, -99999, 99999, -99999
    buffers: list[PayloadBuffer | BatchBuilder] = item_warehouse.input_buffers
    buffers.extend(item_warehouse.output_buffers)

    # Collect all buffer coordinates
    buffer_coords = []
    for buff in buffers:
        x, y = buff.coordinate[0], buff.coordinate[1]
        buffer_coords.append((x, y))
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    # Detect orientation: buffers on x-axis (top/bottom) or y-axis (left/right)
    unique_x = len(set(x for x, y in buffer_coords))
    unique_y = len(set(y for x, y in buffer_coords))

    # If more variety in x-coordinates, buffers are horizontal (top/bottom)
    # If more variety in y-coordinates, buffers are vertical (left/right)
    buffers_horizontal = unique_x > unique_y

    item_warehouse_item = ItemWarehouseItem(
        top_left_corner_pos=(min_x, min_y),
        bottom_right_corner_pos=(max_x, max_y),
        event_bus=event_bus,
        buffers_horizontal=buffers_horizontal
    )
    # Create dict entry with 'item_warehouse'-key
    component_items["item_warehouse"] = item_warehouse_item




