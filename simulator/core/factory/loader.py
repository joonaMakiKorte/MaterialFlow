from pathlib import Path
import json
import simpy
from simulator.core.components.component import Component
from simulator.core.components.depalletizer import Depalletizer
#from simulator.core.components.junction import Junction
from simulator.core.components.payload_conveyor import PayloadConveyor
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.routing.factory_graph import FactoryGraph
from simulator.core.factory.id_gen import IDGenerator
from simulator.core.stock.warehouse import Warehouse

# Factory registry for components
COMPONENT_TYPES = {
    "PayloadConveyor" : PayloadConveyor,
    "PayloadBuffer" : PayloadBuffer,
    "Depalletizer" : Depalletizer,
    "BatchBuilder" : BatchBuilder
    #"Junction" : Junction
}

def load_factory_from_json(file_path: str,
                           env: simpy.Environment,
                           id_gen: IDGenerator,
                           components: dict[str,Component],
                           factory_graph: FactoryGraph,
                           warehouse: Warehouse):
    """
    Load components from JSON file and return dict mapping component_id -> Component.
    Also handles component connecting and inserting to factory graph.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    # Load components
    for comp_data in config["components"]:
        comp_type = comp_data["type"]
        comp_id = comp_data["id"]

        if comp_type not in COMPONENT_TYPES:
            raise ValueError(f"Unknown component type: {comp_type}")

        cls = COMPONENT_TYPES[comp_type]
        kwargs = {k: v for k, v in comp_data.items() if k not in ("id", "type")}

        # Convert coordinates to tuple if present
        for key in ("coordinate", "start", "end"):
            if key in kwargs:
                coords = kwargs[key]
                if isinstance(coords, list) and len(coords) == 2:
                    kwargs[key] = tuple(coords)
                else:
                    raise ValueError(f"Invalid {key} format for {comp_id}: {coords}")

        # Special handling for different classes
        if comp_type == "BatchBuilder":
            component = cls(env,id_gen, comp_id, **kwargs)
        else :
            component = cls(env,comp_id, **kwargs)

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

    # Load warehouse buffers
    wh_cfg = config.get("stock", {}).get("warehouse")
    if not wh_cfg:
        raise ValueError(f"Warehouse configuration not found in '{file_path}'.")

    input_buffer_id = wh_cfg["input_buffer"]
    if input_buffer_id not in components:
        raise ValueError(f"Input buffer ({input_buffer_id}) not found.")
    warehouse.input_buffer = components[input_buffer_id] # Connect input buffer

    output_buffer_id = wh_cfg["output_buffer"]
    if output_buffer_id not in components:
        raise ValueError(f"Output buffer ({output_buffer_id}) not found.")
    warehouse.output_buffer = components[output_buffer_id] # Connect output buffer


