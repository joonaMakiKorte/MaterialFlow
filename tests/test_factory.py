from simulator.core.factory.factory import Factory
from simulator.core.components.component import Component
from simulator.core.factory.loader import load_factory_from_json
import json

def test_load_factory_from_json(mock_factory_json, env, id_gen, factory_graph, warehouse):
    """Test loading factory layout from json."""
    components: dict[str,Component] = {}
    load_factory_from_json(file_path=mock_factory_json,
                           env=env,
                           id_gen=id_gen,
                           components=components,
                           factory_graph=factory_graph,
                           warehouse=warehouse)

    # Load the reference mock JSON
    with open(mock_factory_json) as f:
        mock_factory = json.load(f)

    # Assert components have been loaded
    assert len(components) == len(mock_factory["components"])

    # Assert all connections can be found in factory graph
    total_edges = sum(len(edges) for edges in factory_graph._adjacency.values())
    assert total_edges == len(mock_factory["connections"])

    assert warehouse.input_buffer.id == mock_factory.get("stock", {}).get("warehouse")["input_buffer"]
