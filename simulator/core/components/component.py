import simpy
from typing import List
from abc import ABC, abstractmethod

class Component(ABC):
    """
    Abstract base class for all factory system components.

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
    process : simpy.Process
        SimPy process instance for this component.
    """
    def __init__(self, env: simpy.Environment, component_id : int, name: str):
        self.env = env
        self.component_id = component_id
        self.name = name
        self.downstream: List["Component"] = []

        # Register run loop
        self.process = env.process(self.run())

    def connect(self, downstream_components: List["Component"]):
        """Link component's output to another components (can be overridden)."""
        self.downstream.extend(downstream_components)

    @abstractmethod
    def run(self):
        """Main component loop for the SimPy process."""

    @abstractmethod
    def can_load(self) -> bool:
        """Check if component is free for loading"""
        pass

    @abstractmethod
    def load(self, payload: object):
        """Load payload on component. Implementation depends on component type"""
        pass
