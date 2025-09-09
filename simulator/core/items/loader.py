from pathlib import Path
import json
from simulator.core.items.item import Item

def load_items_from_json(file_path: str) -> dict[int, Item]:
    """
    Load items from JSON file and return a dictionary mapping item_id -> Item
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {entry["item_id"]: Item(**entry) for entry in data}