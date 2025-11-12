from PyQt6.QtCore import QTimer, QObject, pyqtSlot, pyqtSignal
import simpy
import time
from simulator.gui.factory_scene import FactoryScene
from simulator.core.utils.event_bus import EventBus


class SimulationController(QObject):
    """
    Controls simulation running with real-time pacing.
    Listens for simulation events and persists them to the factory scene.
    """
    time_changed = pyqtSignal(int)
    speed_changed = pyqtSignal(float)

    def __init__(self, env: simpy.Environment, scene: FactoryScene):
        super().__init__()
        self.env = env
        self.scene = scene
        self.event_bus: EventBus = scene.event_bus

        # Simulation speed settings
        self.speeds = [0.5, 1.0, 1.5, 3.0]
        self.speed_index = 1  # Default to 1.0x

        # Timer for stepping the simulation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.running = False
        self.last_tick_real_time = 0

        # Interval for GUI smoothness. 20ms = 50 updates/sec
        self.gui_update_interval_ms = 20

    def setup_subscriptions(self):
        """Subscribe to relevant events from the simulation."""
        self.event_bus.subscribe("dispatch_pallet", self.on_dispatch_pallet)
        self.event_bus.subscribe("store_payload", self.on_store_payload)
        self.event_bus.subscribe("move_payload", self.on_move_payload)
        self.event_bus.subscribe("update_payload", self.on_update_payload_state)
        self.event_bus.subscribe("create_batch", self.on_create_batch)

    def start(self):
        if self.running:
            return
        self.running = True
        # Record the current real time to calculate elapsed time in the first tick
        self.last_tick_real_time = time.time()
        self.timer.start(self.gui_update_interval_ms)

    def stop(self):
        self.running = False
        self.timer.stop()

    def change_speed(self):
        """Cycles to the next speed."""
        self.speed_index = (self.speed_index + 1) % len(self.speeds)
        new_speed = self.speeds[self.speed_index]
        self.speed_changed.emit(new_speed)

    @pyqtSlot()
    def tick(self):
        """
        Advances the simulation based on the real time that has passed since the last tick.
        This ensures 1 simulation unit = 1 second at 1.0x speed.
        """
        if not self.running:
            return

        current_real_time = time.time()
        real_time_elapsed = current_real_time - self.last_tick_real_time
        self.last_tick_real_time = current_real_time

        # Get the current speed multiplier
        current_speed_multiplier = self.speeds[self.speed_index]

        # Calculate how much simulation time should pass
        # At 1.0x speed, sim_time_to_advance = real_time_elapsed
        sim_time_to_advance = real_time_elapsed * current_speed_multiplier
        target_sim_time = self.env.now + sim_time_to_advance

        try:
            # Run the simulation until the calculated target time
            self.env.run(until=target_sim_time)
            self.time_changed.emit(int(self.env.now))

            # Check if the simulation has finished
            if self.env.peek() == float('inf'):
                print("Simulation completed.")
                self.stop()

        except simpy.core.EmptySchedule:
            print("Simulation completed (empty schedule).")
            self.stop()

    # --------------
    # Event handlers
    # --------------

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