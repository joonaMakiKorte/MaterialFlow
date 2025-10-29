import simpy
import heapq
from collections import deque
from typing import Deque
from abc import ABC, abstractmethod
from simulator.core.orders.order import Order
from simulator.gui.event_bus import EventBus
import itertools
from simulator.core.factory.log_manager import get_logger
from simulator.config import MAX_COMPONENT_LOG_COUNT

class Stock(ABC):
    """
    Abstract base class for inventory management elements of the factory system.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    process_order_main : simpy.Environment
        SimPy process instance for monitoring and processing orders
    order_queue : min-heap
        Internal priority queue for handling orders based on priority.
    logger : logging.Logger
        Logging manager for the component.
    recent_logs : list[str]
        Store a constricted amount of recent logs.
    """
    _counter = itertools.count()  # shared counter across all instances

    def __init__(self, env: simpy.Environment, name: str):
        self.env = env
        self.process_order_main = self.env.process(self._order_loop())
        self._order_queue = []
        self.event_bus: None | EventBus = None

        # Configure logger
        self._recent_logs: Deque[str] = deque(maxlen=MAX_COMPONENT_LOG_COUNT)
        self._logger = get_logger(name, self._recent_logs)


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
    def inject_eventbus(self, event_bus: EventBus):
        pass

    @abstractmethod
    def _order_loop(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"