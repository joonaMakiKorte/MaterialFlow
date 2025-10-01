from simulator.core.items.loader import load_items_from_json
from simulator.core.items.item import Item
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
    def __init__(self, json_name: str):
        self._items = self._load_items(json_name)

    # -----------------
    # Dict-like access
    # -----------------

    def __getitem__(self, item_id: int) -> Item:
        return self._items[item_id]

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self):
        return len(self._items)

    # -----------------
    # Private helpers
    # -----------------

    def _load_items(self, json_name: str) -> dict[int, Item]:
        project_root = Path(__file__).parent.parent.parent.parent
        json_path = project_root / "data" / json_name
        return load_items_from_json(str(json_path))

    # ---------------
    # Public methods
    # ---------------

    def qty_per_pallet(self, item_id: int, pallet_volume: float, pallet_weight_limit: float) -> int:
        """Compute max items per pallet given pallet constraints."""
        item = self._items[item_id]
        max_by_volume = pallet_volume // item.volume
        max_by_weight = pallet_weight_limit // item.weight
        return int(min(max_by_volume, max_by_weight))