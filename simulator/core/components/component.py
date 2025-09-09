from typing import List, Tuple

class Component:
    """
    Abstract base class for all factory system components.

    Attributes
    ----------
    component_id : int
        Unique identifier for the component.
    name : str
        Name for the component.
    coordinates : List[Tuple[int,int]]
        List of the coordinates the component occupies on the factory floor.
    """
    def __init__(self, component_id: int, name: str, coordinates: List[Tuple[int, int]]):
        self._component_id = component_id
        self._name = name
        self._coordinates = coordinates