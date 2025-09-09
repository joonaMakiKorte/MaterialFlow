from pathlib import Path
from simulator.core.items.loader import load_items_from_json
from simulator.core.items.item import Item

def test_load_items_from_json(tmp_path):
    # Path to JSON file
    project_root = Path(__file__).parent.parent
    json_path = project_root / "data" / "items.json"

    # Make sure JSON exists
    assert json_path.exists(), f"{json_path} does not exist"

    # Load items
    items_dict = load_items_from_json(str(json_path))

    # Assert basic properties
    assert isinstance(items_dict, dict)
    assert len(items_dict) > 0

    # Check that entities have basic attributes
    first_item = next(iter(items_dict.values()))
    assert isinstance(first_item, Item)
    assert hasattr(first_item, "item_id")
    assert hasattr(first_item, "name")

