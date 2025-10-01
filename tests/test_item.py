import json
from simulator.core.items.loader import load_items_from_json
from simulator.core.items.item import Item


def test_load_items_from_json(mock_items_json):
    # Load items
    items_dict = load_items_from_json(str(mock_items_json))

    # Load the reference mock JSON
    with open(mock_items_json) as f:
        mock_items = json.load(f)

    # Assert basic properties
    assert isinstance(items_dict, dict)
    assert len(items_dict) == len(mock_items)

    # Compare items against mock JSON
    for mock in mock_items:
        item = items_dict[mock["item_id"]]
        assert isinstance(item, Item)

        # Compare all properties
        assert item.item_id == mock["item_id"]
        assert item.name == mock["name"]
        assert item.weight == mock["weight"]
        assert item.category == mock["category"]
        assert item.volume == mock["volume"]
        assert item.stackable == mock["stackable"]

def test_catalogue(catalogue, mock_items_json):
    # Load the reference mock JSON
    with open(mock_items_json) as f:
        mock_items = json.load(f)

    # Basic catalogue checks
    assert isinstance(catalogue._items, dict)
    assert len(catalogue) == len(mock_items)

    # Check that iteration works
    first_item = next(iter(catalogue))
    assert isinstance(first_item, Item)
    assert isinstance(first_item.volume, float)
    assert isinstance(first_item.stackable, bool)
