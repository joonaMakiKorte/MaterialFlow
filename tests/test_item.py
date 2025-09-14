from pathlib import Path
from simulator.core.items.loader import load_items_from_json
from simulator.core.items.item import Item
from simulator.core.items.catalogue import Catalogue

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

def test_catalogue():
    # Init catalogue
    catalogue = Catalogue()

    # Assert basic properties
    assert isinstance(catalogue.items, dict)
    assert len(catalogue.items) > 0

    # Check that entities have basic attributes and methods work
    first_item_id = next(iter(catalogue.items.values())).item_id
    assert isinstance(catalogue.get_item(first_item_id), Item)
    assert isinstance(catalogue.get_volume(first_item_id), float)
    assert isinstance(catalogue.is_stackable(first_item_id), bool)
