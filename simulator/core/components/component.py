import simpy
from abc import ABC, abstractmethod
from simulator.gui.event_bus import EventBus

class Component(ABC):
    """
    Abstract base class for all factory systems physical flow elements.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    component_id : str
        Unique identifier for the component.
    type : str
        The component type.
    static_process_time : float
        The base process time of the component
    output : Component
        A default single output for component.
    outputs : dict[str,Component]
        Allow named outputs for components with multiple.
    event_bus : EventBus
        Bridge to communicate with gui.
    """
    def __init__(self, env: simpy.Environment, component_id: str, static_process_time: float):
        self.env = env
        self._component_id = component_id
        self._type = self.__class__.__name__
        self._static_process_time = static_process_time
        self._output: None | Component = None
        self._outputs: dict[str, "Component"] = {}
        self.event_bus: None | EventBus = None

    # ----------
    # Properties
    # ----------

    @property
    def id(self) -> str:
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

    # ---------
    #   Logic
    # ---------

    def connect(self, component: "Component", port: str = "out"):
        """Link component's output to another components. Overridable"""
        if port == "out":
            self._output = component
        else:
            self._outputs[port] = component

    @abstractmethod
    def can_load(self) -> bool:
        """Check if component is free for loading"""
        pass

    @abstractmethod
    def load(self, payload):
        """Load payload on component. Implementation depends on component type"""
        pass

    def inject_event_bus(self, event_bus: EventBus):
        """Inject event bus. Overloadable"""
        self.event_bus = event_bus

    def __repr__(self):
        return f"{self._type}(id={self._component_id})"