from simulator.core.items.loader import load_items_from_json
from pathlib import Path

class Catalogue:
    """
    Stores item master data (in-memory product catalogue).
    Provides fast lookup of items by ID.
    Exposes helper methods for order-related calculations.

    Attributes
    ----------
    items : dict[int,Item]
        Items are stored in a dictionary keyed by item_id
    """
    def __init__(self):
        def load_items():
            # Path to JSON file
            project_root = Path(__file__).parent.parent.parent.parent
            json_path = project_root / "data" / "items.json"

            # Load items
            return load_items_from_json(str(json_path))

        self.items = load_items()

    def get_item(self, item_id: int):
        """Retrieve full item record."""
        return self.items.get(item_id, None)

    def get_volume(self, item_id: int):
        return self.items[item_id].volume

    def get_weight(self, item_id: int):
        return self.items[item_id].weight

    def is_stackable(self, item_id: int):
        return self.items[item_id].stackable

    def qty_per_pallet(self, item_id: int, pallet_volume: float, pallet_weight_limit: float):
        """Compute max items per pallet given pallet constraints."""
        item = self.items[item_id]
        max_by_volume = pallet_volume // item.volume
        max_by_weight = pallet_weight_limit // item.weight
        return int(min(max_by_volume, max_by_weight))