import simpy
from typing import Optional
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
    output : Component
        A default single output for component.
    outputs : dict[str,Component]
        Allow named outputs for components with multiple.
    """
    def __init__(self, env: simpy.Environment, component_id : int):
        self.env = env
        self._component_id = component_id
        self._output: Optional["Component"] = None
        self._outputs: dict[str, "Component"] = {}

    # ----------
    # Properties
    # ----------

    @property
    def id(self) -> int:
        return self._component_id

    @property
    def output(self) -> "Component":
        return self._output

    # ---------
    #   Logic
    # ---------

    def connect(self, component: "Component", port: str = "out"):
        """Link component's output to another components."""
        if port == "out":
            self._output = component
        else:
            self._outputs[port] = component

    @abstractmethod
    def can_load(self) -> bool:
        """Check if component is free for loading"""
        pass

    @abstractmethod
    def load(self, payload: object):
        """Load payload on component. Implementation depends on component type"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._component_id})"