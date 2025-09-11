from typing import Tuple, Optional

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
    desired_dest: Tuple[float,float]
        Destination to transport the pallet to. A pair of component id and slot id (e.g., 'Conveyor-01, slot 2')
    actual_dest: Tuple[float,float]
        Current destination of the pallet.
    """
    def __init__(self, pallet_id: int, actual_dest: Tuple[float,float]):
        self.pallet_id = pallet_id
        self.order_id: Optional[int] = None
        self.desired_dest: Optional[Tuple[float,float]] = None
        self.actual_dest = actual_dest

    def __repr__(self):
        return f"Pallet({self.pallet_id})"