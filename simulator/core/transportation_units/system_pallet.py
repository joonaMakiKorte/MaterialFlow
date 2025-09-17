from typing import Optional, Tuple
from dataclasses import dataclass
from simulator.core.orders.order import Order

@dataclass
class Destination:
    """Logical destination request."""
    type: str  # e.g., "depalletizer", "storage", "dock"
    id: str | None = None  # optional: specific resource ID

@dataclass
class Location:
    """Concrete location of the pallet"""
    element_name: str  # e.g. "Depalletizer_3"
    coordinates: Tuple[float, float]  # (x, y)

    def update(self, coordinates: Tuple[float, float], element_name: Optional[str] = None):
        """Update location. Allow element name overriding"""
        self.coordinates = coordinates
        if element_name is not None:
            self.element_name = element_name

class SystemPallet:
    """
    Represents a transport pallet moving on conveyors.
    Has a unique identifier, may carry an order.

    Attributes:
    ----------
    pallet_id : int
        Unique identifier.
    order : Order
        Assigned order. Value is 'None' if no order assigned.
    requested_dest: Destination
        Destination to transport the pallet to. Value is 'None' if no ordered destination.
    actual_location: Location
        Concrete location of the pallet.
    """
    def __init__(self, pallet_id: int, actual_location: Location):
        self._pallet_id = pallet_id
        self._order: Optional[Order] = None
        self.requested_dest: Optional[Destination] = None
        self.actual_location = actual_location

    # ----------
    # Properties
    # ----------

    @property
    def pallet_id(self) -> int:
        return self._pallet_id

    @property
    def order(self) -> Order:
        return self._order

    @order.setter
    def order(self, new_order):
        """Set a new order with validation (or clear with None)."""
        if new_order is not None and not isinstance(new_order, Order):
            raise ValueError("order must be an Order or None")
        self._order = new_order

    # ---------------
    # Public methods
    # ---------------

    def __repr__(self):
        return f"{self.__class__.__name__}({self.pallet_id})"