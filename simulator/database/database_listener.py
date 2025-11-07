from simulator.database.database_manager import DatabaseManager
from simulator.core.utils.event_bus import EventBus

class DatabaseListener:
    """Listens for simulation events and persists them to the database"""
    def __init__(self, event_bus: EventBus, db_manager: DatabaseManager):
        self.event_bus = event_bus
        self.db_manager = db_manager

    def setup_subscriptions(self):
        """Subscribe to relevant events from the simulation."""
        self.event_bus.subscribe("pallet_created", self.on_pallet_created)
        self.event_bus.subscribe("update_payload", self.on_pallet_updated)
        self.event_bus.subscribe("store_payload", self.on_pallet_moved)
        self.event_bus.subscribe("move_payload", self.on_pallet_moved)

    def on_pallet_created(self, data: dict):
        self.db_manager.insert_pallet(
            pallet_id=data['pallet_id'],
            location=data['location'],
            sim_time=data['sim_time']
        )

    def on_pallet_updated(self, data: dict):
        """Updates assigned order and destination on pallet"""
        if data.get("type") != "SystemPallet":
            # Assert we only update data if type is SystemPallet
            return

        self.db_manager.update_pallet(
            pallet_id=data['id'],
            sim_time=data['sim_time'],
            order_id=data['order_id'],
            destination=data['destination']
        )

    def on_pallet_moved(self, data: dict):
        """""""Update pallet location and destination"""
        if data.get("type") != "SystemPallet":
            return

        self.db_manager.update_pallet(
            pallet_id=data['id'],
            sim_time=data['sim_time'],
            location=data['location']
        )