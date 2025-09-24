import simpy
import heapq
from abc import ABC, abstractmethod
from simulator.core.orders.order import Order

class Stock(ABC):
    """
    Abstract base class for inventory management elements of the factory system.

    Attributes
    ----------
    env : simpy.Environment
        Simulation environment.
    process : simpy.Process
        SimPy process instance for this component.
    stock_id : int
        Unique identifier.
    order_queue : min-heap[int, Order]
        Internal priority queue for handling orders based on priority.
    """
    def __init__(self, stock_id: int):
        self.env = None
        self.process = None
        self._stock_id = stock_id
        self._order_queue = []

    # ----------
    # Properties
    # ----------

    @property
    def stock_id(self) -> int:
        return self._stock_id

    # ---------------
    # Private helpers
    # ---------------

    def _next_order(self):
        """Pop the next order (highest priority)."""
        if self._order_queue:
            return heapq.heappop(self._order_queue)[1]
        return None

    def _has_orders(self) -> bool:
        return len(self._order_queue) > 0

    # ----------
    #   Logic
    # ----------

    def inject_env(self, env: simpy.Environment):
        self.env = env
        self.process = env.process(self._run())  # Register run loop

    def place_order(self, order: Order, priority: int):
        """Insert an order with given priority (lower = higher priority)."""
        heapq.heappush(self._order_queue, (priority, order))

    @abstractmethod
    def process_order(self, order: Order):
        """Order processing depends on the stock type."""
        pass

    @abstractmethod
    def _run(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.stock_id})"