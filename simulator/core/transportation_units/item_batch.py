import simpy
from simulator.core.transportation_units.transportation_unit import TransportationUnit, Location
from simulator.config import MAX_ITEM_BATCH


class ItemBatch(TransportationUnit):
    """
    A transportation unit for a group of items moving on an item carrier.
    May contain multiple different items.

    Additional Attributes
    ---------------------
    items : dict[int,int]
        Item quantities are stored in a dict mapped by item-id.
    ready_event : simpy.events.Event
        Event triggered when the batch is full, or when the last item of order gets loaded.
    """
    def __init__(self, batch_id: int, actual_location: Location):
        super().__init__(batch_id, actual_location)
        self._items: dict[int,int] = {}
        self._item_count = 0
        self.ready_event = None

    # ----------
    # Properties
    # ----------

    @property
    def item_count(self) -> int:
        return self._item_count

    @property
    def items(self) -> dict[int, int]:
        return dict(self._items)

    # -----------------
    # Dict-like access
    # -----------------

    def __getitem__(self, item_id: int) -> int:
        return self._items[item_id]

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self):
        return len(self._items)

    # --------------
    # Public methods
    # --------------

    def add_item(self, item_id: int):
        """Add one item to the batch."""
        # Increment quantities
        self._items[item_id] = self._items.get(item_id, 0) + 1
        self._item_count += 1

        # Check if batch is ready
        if (self._item_count >= MAX_ITEM_BATCH) and not self.ready_event.triggered:
            self.ready_event.succeed(self)

    def handoff(self):
        """ Manually trigger batch-ready event"""
        self.ready_event.succeed(self)