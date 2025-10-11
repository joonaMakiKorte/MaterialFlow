from abc import ABC
from datetime import datetime
from enum import Enum, auto
from typing import Dict

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
    type : str
        Type of order. (refill/OPM)
    order_time : datetime
        Timestamp of the order creation.
    status : OrderStatus
        Current processing state.
    """

    def __init__(self, order_id: int):
        self._order_id = order_id
        self._type = self.__class__.__name__
        self._order_time = datetime.now()
        self._status = OrderStatus.PENDING

    # ----------
    # Properties
    # ----------

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def type(self) -> str:
        return self._type

    @property
    def order_time(self) -> datetime:
        return self._order_time

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, new_status):
        """Set a new order status with validation."""
        if not isinstance(new_status, OrderStatus):
            raise ValueError("status must be an OrderStatus enum")
        self._status = new_status

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.order_id}, status={self.status.name})"


class RefillOrder(Order):
    """
    Type of Order to move stock from Warehouse to ItemWarehouse.

    Additional attributes
    ----------
    item_id : int
        Id of the Item contained in the pallet
    qty : int
        Amount of items in the pallet / quantity requested
    """
    def __init__(self, order_id: int, item_id: int, qty: int):
        super().__init__(order_id)
        self._item_id = item_id
        self._qty = qty

    # ----------
    # Properties
    # ----------

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def qty(self) -> int:
        return self._qty


class OpmOrder(Order):
    """
    Order from ItemWarehouse to OPM.

    Additional attributes
    ----------
    requested_items: Dict[int, int]
        Contents of the order with quantities
    """
    def __init__(self, order_id: int, requested_items: Dict[int, int]):
        super().__init__(order_id)
        self.requested_items = requested_items
