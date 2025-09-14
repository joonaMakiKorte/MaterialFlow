import simpy
from typing import List
from abc import ABC, abstractmethod

class Component(ABC):
    """
    Abstract base class for all factory systems physical flow elements.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    component_id : int
        Unique identifier for the component.
    name : str
        Human-readable name of the component.
    downstream : List[Component]
        List of linked downstream components.
    """
    def __init__(self, env: simpy.Environment, component_id : int, name: str):
        self.env = env
        self.component_id = component_id
        self.name = name
        self.downstream: List["Component"] = []

    def connect(self, downstream_components: List["Component"]):
        """Link component's output to another components (can be overridden)."""
        self.downstream.extend(downstream_components)

    @abstractmethod
    def can_load(self) -> bool:
        """Check if component is free for loading"""
        pass

    @abstractmethod
    def load(self, payload: object):
        """Load payload on component. Implementation depends on component type"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.component_id}, name={self.name})"