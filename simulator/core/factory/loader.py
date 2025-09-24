from pathlib import Path
import json
import simpy

from simulator.core.components.component import Component
from simulator.core.components.depalletizer import Depalletizer
from simulator.core.components.item_conveyor import ItemConveyor
from simulator.core.components.junction import Junction
from simulator.core.components.pallet_conveyor import PalletConveyor
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.routing.factory_graph import FactoryGraph

# Factory registry for components
COMPONENT_TYPES = {
    "PalletConveyor" : PalletConveyor,
    "ItemConveyor" : ItemConveyor,
    "PayloadBuffer" : PayloadBuffer,
    "Depalletizer" : Depalletizer,
    "Junction" : Junction
}

def load_components_from_json(file_path: str, factory_graph: FactoryGraph) -> dict[int, Component]:
    """
    Load components from JSON file and return dict mapping component_id -> Component.
    Also handles component connecting and inserting to factory graph.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    # Load components
    components = {}
    for comp_data in config["components"]:
        comp_type = comp_data["type"]
        comp_id = comp_data["id"]

        if comp_type not in COMPONENT_TYPES:
            raise ValueError(f"Unknown component type: {comp_type}")

        cls = COMPONENT_TYPES[comp_type]

        # Create component instance
        kwargs = {k: v for k, v in comp_data.items() if k not in ("id", "type")}
        component = cls(comp_id, **kwargs)

        # Add to dict and graph
        components[comp_id] = component
        factory_graph.add_node(comp_id)

    # Load connections
    for conn in config["connections"]:
        src_id = conn["from"]
        dst_id = conn["to"]
        port_type = conn["port"]

        if src_id not in components or dst_id not in components:
            raise ValueError(f"Invalid connection: {src_id} -> {dst_id}")

        # Connect components
        src = components[src_id]
        dst = components[dst_id]
        src.connect(dst, port_type)

        # Add as edge to graph
        factory_graph.add_edge(
            source_id=src_id,
            target_id=dst_id,
            target_type=dst.type,
            base_weight=src.static_process_time)

    return components