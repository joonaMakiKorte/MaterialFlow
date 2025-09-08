class SystemPallet:
    """
    Represents a transport pallet moving on conveyors.
    Has a unique identifier, may carry an order.

    Attributes:
    ----------
    pallet_id : int
        Unique identifier.
    order_id : int
        Id of the assigned order. Is given value -1 if no order assigned.
    desired_dest: ?
        Destination to transport the pallet to.
    actual_dest: ?
        Current destination of the pallet.
    """
