from simulator.core.location import Location
from typing import Optional


class SystemPallet:
    """
    Represents a transport pallet moving on conveyors.
    Has a unique identifier, may carry an order.

    Attributes:
    ----------
    pallet_id : int
        Unique identifier.
    order_id : int
        Id of the assigned order. Value is 'None' if no order assigned.
    desired_dest: Location
        Destination to transport the pallet to. Value is 'None' if no requested transportation orders.
    actual_dest: Location
        Current destination of the pallet.
    """
    def __init(self, pallet_id: int, current_dest: Location):
        self._pallet_id = pallet_id
        self._order_id: Optional[int] = None
        self._desired_dest: Optional[Location] = None
        self._current_dest = current_dest
