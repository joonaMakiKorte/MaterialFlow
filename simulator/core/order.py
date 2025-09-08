from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Dict
from simulator.core.item import Item

class OrderStatus(Enum):
    """Enumeration of possible order states."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()


class Order(ABC):
    """
    Abstract base class for all orders in the material flow system.

    Attributes
    ----------
    order_id : int
        Unique identifier for the order.
    order_time : datetime
        Timestamp of the order creation.
    status : OrderStatus
        Current processing state.
    """

    def __init__(self, order_id: int):
        self._order_id = order_id
        self._order_time = datetime.now()
        self._status = OrderStatus.PENDING

    @property
    def status(self) -> OrderStatus:
        return self._order_status

    @status.setter
    def status(self, new_status):
        """Set a new order status with validation."""
        if not isinstance(new_status, OrderStatus):
            raise ValueError("status must be an OrderStatus enum")
        self._status = new_status

    @abstractmethod
    def process(self):
        # Orders are processed differently depending on the type
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.order_id}, status={self.status.name})"


class RefillOrder(Order):
    """
    Type of Order to move stock from Warehouse to ItemWarehouse.

    Additional attributes
    ----------
    item : Item
        Item contained in the pallet
    item_count : int
        Amount of items in the pallet / quantity requested
    """
    def __init__(self, order_id: int, item: Item, qty_requested: int):
        super().__init__(order_id)
        self._item = item
        self._item_count = qty_requested

    def process(self):
        """TODO"""


class OpmOrder(Order):
    """
    Order from ItemWarehouse to OPM.

    Additional attributes
    ----------
    requested_items: Dict[Item, int]
        Contents of the order with counts
    """
    def __init__(self, order_id: int, requested_items: Dict[Item, int]):
        super().__init__(order_id)
        self._requested_items = requested_items

    def process(self):
        """TODO"""
