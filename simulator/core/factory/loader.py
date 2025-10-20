from pathlib import Path
import json
import simpy
from simulator.core.components.component import Component
from simulator.core.components.depalletizer import Depalletizer
from simulator.core.components.payload_conveyor import PayloadConveyor
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.components.junction import Junction
from simulator.core.factory.id_gen import IDGenerator
from simulator.core.stock.warehouse import Warehouse
from simulator.core.stock.item_warehouse import ItemWarehouse

# Factory registry for components
COMPONENT_TYPES = {
    "PayloadConveyor": PayloadConveyor,
    "PayloadBuffer": PayloadBuffer,
    "Depalletizer": Depalletizer,
    "BatchBuilder": BatchBuilder,
    "Junction": Junction
}

def load_factory_from_json(
        file_path: str,
        env: simpy.Environment,
        id_gen: IDGenerator,
        components: dict[str, Component],
        warehouse: Warehouse,
        item_warehouse: ItemWarehouse
):
    """
    Load components from JSON file and return dict mapping component_id -> Component.
    Also handles component connecting and inserting to factory graph.
    """
    config = _load_config(file_path)

    _load_components(config, env, id_gen, components)
    _load_connections(config, components)
    _configure_warehouse(config, components, warehouse)
    _configure_item_warehouse(config, components, item_warehouse)


def _load_config(file_path: str) -> dict:
    """Load and return JSON configuration."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_components(
        config: dict,
        env: simpy.Environment,
        id_gen: IDGenerator,
        components: dict[str, Component]
):
    """Create components from config and add to registry."""
    for comp_data in config["components"]:
        comp_type = comp_data["type"]
        comp_id = comp_data["id"]

        if comp_type not in COMPONENT_TYPES:
            raise ValueError(f"Unknown component type: {comp_type}")

        cls = COMPONENT_TYPES[comp_type]
        kwargs = {k: v for k, v in comp_data.items() if k not in ("id", "type", "ratio")}

        # Convert coordinate lists to tuples
        _convert_coordinates(kwargs, comp_id)

        # Instantiate component with appropriate constructor
        if comp_type == "BatchBuilder":
            component = cls(env, id_gen, comp_id, **kwargs)
        elif comp_type == "Junction":
            ratio = comp_data["ratio"]
            component = cls(env, comp_id, ratio, **kwargs)
        else:
            component = cls(env, comp_id, **kwargs)

        components[comp_id] = component


def _convert_coordinates(kwargs: dict, comp_id: str):
    """Convert coordinate lists to tuples in-place."""
    for key in ("coordinate", "start", "end"):
        if key in kwargs:
            coords = kwargs[key]
            if isinstance(coords, list) and len(coords) == 2:
                kwargs[key] = tuple(coords)
            else:
                raise ValueError(f"Invalid {key} format for {comp_id}: {coords}")


def _load_connections(
        config: dict,
        components: dict[str, Component]
):
    """Establish connections between components."""
    for conn in config["connections"]:
        src_id = conn["from"]
        dst_id = conn["to"]
        port_type = conn["port"]

        if src_id not in components or dst_id not in components:
            raise ValueError(f"Invalid connection: {src_id} -> {dst_id}")

        src = components[src_id]
        dst = components[dst_id]

        src.connect(dst, port_type)


def _configure_warehouse(config: dict, components: dict[str, Component], warehouse: Warehouse):
    """Configure warehouse input and output buffers."""
    wh_cfg = config.get("stock", {}).get("warehouse")
    if not wh_cfg:
        raise ValueError("Warehouse configuration not found.")

    warehouse.input_buffer = _get_buffer(components, wh_cfg["input_buffer"], "Input")
    warehouse.output_buffer = _get_buffer(components, wh_cfg["output_buffer"], "Output")


def _configure_item_warehouse(
        config: dict,
        components: dict[str, Component],
        itemwarehouse: ItemWarehouse
):
    """Configure item warehouse input and output buffers."""
    iwh_cfg = config.get("stock", {}).get("item_warehouse")
    if not iwh_cfg:
        raise ValueError("ItemWarehouse configuration not found.")

    for buffer_id in iwh_cfg["input_buffers"]:
        buffer = _get_buffer(components, buffer_id, "Input")
        itemwarehouse.inject_input_buffer(buffer)

    for buffer_id in iwh_cfg["output_buffers"]:
        buffer = _get_buffer(components, buffer_id, "Output")
        itemwarehouse.inject_output_buffer(buffer)


def _get_buffer(components: dict[str, Component], buffer_id: str, buffer_type: str) -> Component:
    """Retrieve buffer component or raise error."""
    buffer = components.get(buffer_id)
    if not buffer:
        raise ValueError(f"{buffer_type} buffer ({buffer_id}) not found.")
    return buffer
