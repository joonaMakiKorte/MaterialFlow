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
    type : str
        The component type.
    static_process_time : float
        The base process time of the component
    output : Component
        A default single output for component.
    outputs : dict[str,Component]
        Allow named outputs for components with multiple.
    """
    def __init__(self, component_id : int):
        self.env = None
        self._component_id = component_id
        self._type = self.__class__.__name__
        self._static_process_time = None # Initialized for each component type individually
        self._output: Optional["Component"] = None
        self._outputs: dict[str, "Component"] = {}

    # ----------
    # Properties
    # ----------

    @property
    def id(self) -> int:
        return self._component_id

    @property
    def type(self) -> str:
        return self._type

    @property
    def static_process_time(self) -> float:
        return self._static_process_time

    @property
    def output(self) -> "Component":
        return self._output

    # ---------------
    # Private helpers
    # ---------------

    @abstractmethod
    def _get_static_process_time(self) -> float:
        """Base process time. Depends on component type"""
        pass

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
    def inject_env(self, env: simpy.Environment):
        pass

    @abstractmethod
    def can_load(self) -> bool:
        """Check if component is free for loading"""
        pass

    @abstractmethod
    def load(self, payload: object):
        """Load payload on component. Implementation depends on component type"""
        pass

    def __repr__(self):
        return f"{self._type}(id={self._component_id})"