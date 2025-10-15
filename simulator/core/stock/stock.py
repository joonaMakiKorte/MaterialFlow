import simpy
import heapq
from abc import ABC, abstractmethod
from simulator.core.orders.order import Order
from simulator.gui.event_bus import EventBus
import itertools

class Stock(ABC):
    """
    Abstract base class for inventory management elements of the factory system.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    process : simpy.Process
        SimPy process instance for this component.
    order_queue : min-heap
        Internal priority queue for handling orders based on priority.
    """
    _counter = itertools.count()  # shared counter across all instances

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.process = env.process(self._run())  # Register run loop
        self._order_queue = []
        self.event_bus: None | EventBus = None

    # ---------------
    # Private helpers
    # ---------------

    def _next_order(self):
        """Pop the next order (highest priority)."""
        if self._order_queue:
            return heapq.heappop(self._order_queue)[2]
        return None

    def _has_orders(self) -> bool:
        return len(self._order_queue) > 0

    # ----------
    #   Logic
    # ----------

    @abstractmethod
    def place_order(self, order: Order, priority: int):
        pass

    @abstractmethod
    def process_order(self, order: Order):
        pass

    @abstractmethod
    def inject_eventbus(self, event_bus: EventBus):
        pass

    @abstractmethod
    def _run(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"