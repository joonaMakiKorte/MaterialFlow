from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Item:
    """
    Represents a stock keeping unit in the simulator.
    Has intrinsic properties.
    """
    item_id: int
    name: str
    weight: float   # kg
    category: str   # determines storing location
    volume: float   # liters
    stackable: bool

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id={self.item_id}, name='{self.name}', "
            f"weight={self.weight}, category='{self.category}')"
        )