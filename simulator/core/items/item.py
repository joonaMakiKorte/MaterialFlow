class Item:
    """
    Represents a stock keeping unit in the simulator.
    Has intrinsic properties.

    Attributes.
    ----------
    item_id : int
        Unique identifier for the item.
    name : str
        Item name.
    weight : float
        Item weight in kg. Determines storing capabilities.
    category : str
        Item category. Determines storing location in the warehouse.
    """
    def __init__(self, item_id: int, name: str, weight: float, category: str):
        self.item_id = item_id
        self.name = name
        self.weight = weight
        self.category = category

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.item_id}, name='{self.name}', weight={self.weight}, category='{self.category}')"