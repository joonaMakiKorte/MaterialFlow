from PyQt6.QtCore import QTimer, QObject, pyqtSlot
import simpy
from simulator.gui.factory_scene import FactoryScene
from simulator.core.utils.event_bus import EventBus

class SimulationController(QObject):
    """
    Controls simulation running.
    Listens for simulation events and persists them to the factory scene.
    """
    def __init__(self, env: simpy.Environment, scene: FactoryScene):
        super().__init__()
        self.env = env
        self.scene = scene
        self.event_bus: EventBus = scene.event_bus

        # Subscribe to events
        self.event_bus.subscribe("dispatch_pallet", self.on_dispatch_pallet)
        self.event_bus.subscribe("store_payload", self.on_store_payload)
        self.event_bus.subscribe("move_payload", self.on_move_payload)
        self.event_bus.subscribe("update_payload_state", self.on_update_payload_state)
        self.event_bus.subscribe("create_batch", self.on_create_batch)

        # Timer for stepping the simulation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.running = False

    def start(self):
        self.running = True
        self.timer.start(10)  # 20 ticks per second (real time)

    def stop(self):
        self.running = False
        self.timer.stop()

    @pyqtSlot()
    def tick(self):
        """Advance simulation according to sim_speed and update GUI."""
        if not self.running:
            return

        try:
            # Advance until at least one event executes or we reach the target time
            next_event_time = self.env.peek()

            if next_event_time != float('inf'):
                # Step the environment once — SimPy will advance its own now correctly
                self.env.step()
            else:
                # No more events left
                print("Simulation completed.")
                self.stop()

        except simpy.core.EmptySchedule:
            print("Simulation completed (empty schedule).")
            self.stop()

    # --------------------------
    # Connect events to handlers
    # --------------------------

    def on_dispatch_pallet(self, data):
        pallet_id = data["id"]
        self.scene.create_payload(pallet_id, payload_type="SystemPallet")

    def on_store_payload(self, data):
        pallet_id = data["id"]
        self.scene.delete_payload(pallet_id)

    def on_move_payload(self, data):
        payload_id = data["id"]
        new_pos = data["coords"]
        self.scene.update_payload_position(payload_id, new_pos)

    def on_update_payload_state(self, data):
        payload_id = data["id"]
        new_state = data["state"]
        self.scene.update_payload_state(payload_id, new_state)

    def on_create_batch(self, data):
        batch_id = data["id"]
        self.scene.create_payload(batch_id, payload_type="ItemBatch")