from abc import ABC
from dataclasses import dataclass

@dataclass
class Destination:
    """Logical destination request."""
    type: str  # e.g., "Depalletizer, Storage, None"
    id: int | None = None  # optional: specific resource ID

    def specify(self, element_id: int):
        """Update specific element id for destination."""
        self.id = element_id

@dataclass
class Location:
    """Concrete location of the transportation unit"""
    element_name: str  # e.g. "Depalletizer_3"
    coordinates: tuple[int,int]  # (x, y)

    def update(self, coordinates: tuple[int,int], element_name: None | str = None):
        """Update location. Allow element name overriding"""
        self.coordinates = coordinates
        if element_name is not None:
            self.element_name = element_name

class TransportationUnit(ABC):
    def __init__(self, unit_id: int, actual_location: Location):
        self._unit_id = unit_id
        self.actual_location = actual_location

    @property
    def id(self) -> int:
        return self._unit_id

    def __repr__(self):
        return f"{self.__class__.__name__}({self._unit_id})"