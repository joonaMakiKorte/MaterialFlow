

class OrderService():
    """
    Interface for placing orders in the material flow system.
    Handles manual order placing from Warehouse->ItemWarehouse (RefillOrder) and ItemWarehouse->OPM (OpmOrder).
    Also supports automatic demand driven RefillOrder generating/dispatching if being subscribed to.

    Attributes
    ----------

    """

