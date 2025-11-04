from simulator.database.database_config import db_manager
from simulator.core.utils.event_bus import EventBus

class DatabaseListener:
    """Listens for simulation events and persists them to the database"""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def setup_subscriptions(self):
        """Subscribe to relevant events from the simulation."""
        pass