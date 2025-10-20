from simulator.core.orders.order import Order
from simulator.core.transportation_units.transportation_unit import TransportationUnit, Destination, Location

class SystemPallet(TransportationUnit):
    """
    Represents a transport pallet moving on conveyors.
    Has a unique identifier, may carry an order.

    Additional Attributes
    ---------------------
    order : Order
        Assigned order. Value is 'None' if no order assigned.
    requested_dest: Destination
        Destination to transport the pallet to. Value is 'None' if no ordered destination.
    """
    def __init__(self, pallet_id: int, actual_location: Location):
        super().__init__(pallet_id, actual_location)
        self._order: Order | None = None
        self.requested_dest: Destination | None = None

    # ----------
    # Properties
    # ----------

    @property
    def order(self) -> Order:
        return self._order

    # ---------------
    # Public methods
    # ---------------

    def merge_order(self, new_order, destination_type: str):
        """Merge order to pallet and request a new destination."""
        self._order = new_order
        self.requested_dest = Destination(destination_type)

    def clear_order(self):
        """Clear current order."""
        self._order = None
        self.requested_dest = None # Also clears destination requests