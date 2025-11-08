from abc import ABC
from enum import Enum, auto

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
    order_time : float
        Timestamp of the order creation as sim time.
    status : OrderStatus
        Current processing state.
    """

    def __init__(self, order_id: int, order_time: float):
        self._order_id = order_id
        self._type = self.__class__.__name__
        self._order_time = order_time
        self._status = OrderStatus.PENDING

    # ----------
    # Properties
    # ----------

    @property
    def id(self) -> int:
        return self._order_id

    @property
    def type(self) -> str:
        return self._type

    @property
    def order_time(self) -> float:
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
        return f"{self.__class__.__name__}(id={self.id}, status={self.status.name})"


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
    def __init__(self, order_id: int, order_time: float, item_id: int, qty: int):
        super().__init__(order_id, order_time)
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
    items: dict[int, int]
        Contents of the order with quantities
    """
    def __init__(self, order_id: int, order_time: float, requested_items: dict[int, int]):
        super().__init__(order_id, order_time)
        self._items = requested_items

    @property
    def items(self) -> dict[int, int]:
        return self._items
