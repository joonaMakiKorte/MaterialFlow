from simulator.core.orders.order import OrderStatus
from simulator.database.database_manager import DatabaseManager
from simulator.core.utils.event_bus import EventBus

class DatabaseListener:
    """Listens for simulation events and persists them to the database"""
    def __init__(self, event_bus: EventBus, db_manager: DatabaseManager):
        self.event_bus = event_bus
        self.db_manager = db_manager

    def setup_subscriptions(self):
        """Subscribe to relevant events from the simulation."""
        self.event_bus.subscribe("create_pallet", self.on_pallet_created)
        self.event_bus.subscribe("update_payload", self.on_pallet_updated)
        self.event_bus.subscribe("store_payload", self.on_pallet_moved)
        self.event_bus.subscribe("move_payload", self.on_pallet_moved)
        self.event_bus.subscribe("create_item", self.on_item_created)
        self.event_bus.subscribe("create_order", self.on_order_created)
        self.event_bus.subscribe("update_order", self.on_order_updated)


    # --------------
    # Event handlers
    # --------------

    def on_item_created(self, data: dict):
        self.db_manager.insert_item(
            item_id=data['item_id'],
            name=data['name'],
            weight=data['weight'],
            category=data['category'],
            volume=data['volume'],
            stackable=data['stackable']
        )

    def on_pallet_created(self, data: dict):
        self.db_manager.insert_pallet(
            pallet_id=data['pallet_id'],
            location=data.get('location'),
            destination=data.get('destination'),
            order_id=data.get('order_id'),
            sim_time=data['sim_time']
        )

    def on_pallet_updated(self, data: dict):
        if data.get("type") != "SystemPallet":
            # Assert we only update data if type is SystemPallet
            return
        self.db_manager.update_pallet(
            pallet_id=data['id'],
            sim_time=data['sim_time'],
            order_id=data.get('order_id'),
            destination=data.get('destination')
        )

    def on_pallet_moved(self, data: dict):
        if data.get("type") != "SystemPallet":
            return

        self.db_manager.update_pallet(
            pallet_id=data['id'],
            sim_time=data['sim_time'],
            location=data.get('location')
        )

    def on_order_created(self, data: dict):
        type = data.get("type")
        if type != "RefillOrder" and type != "OpmOrder":
            return

        order_id=data['order_id']
        order_time = data['order_time']

        if type == "RefillOrder":
            self.db_manager.insert_refill_order(
                order_id=order_id,
                order_time=order_time,
                item_id=data['item_id'],
                qty=data['qty']
            )
        elif type == "OpmOrder":
            self.db_manager.insert_opm_order(
                order_id=order_id,
                order_time=order_time,
                items=data['items']
            )

    def on_order_updated(self, data: dict):
        self.db_manager.update_order(
            order_id=data['order_id'],
            status=data.get('status'),
            completion_time=data.get('completion_time')
        )
