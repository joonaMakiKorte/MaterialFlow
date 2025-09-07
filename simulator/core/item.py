class Item:
    def __init__(self, item_id: int, name: str, weight: float, category: str):
        self.id = item_id
        self.name = name
        self.weight = weight
        self.category = category

    def __repr__(self):
        return f"Item(id={self.id}, name='{self.name}', weight={self.weight}, category='{self.category}')"