from PyQt6.QtCore import QTimer, QObject, pyqtSlot
import simpy
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.event_bus import EventBus

class SimulationController(QObject):
    def __init__(self, env: simpy.Environment, scene: FactoryScene):
        super().__init__()
        self.env = env
        self.scene = scene
        self.event_bus: EventBus = scene.event_bus

        # Subscribe to events
        self.event_bus.subscribe("dispatch_pallet", self.on_dispatch_pallet)
        self.event_bus.subscribe("store_pallet", self.on_store_pallet)
        self.event_bus.subscribe("move_payload", self.on_move_payload)
        self.event_bus.subscribe("update_pallet_state", self.on_update_pallet_state)

        # Timer for stepping the simulation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.sim_speed = 1.0  # can scale simulation speed (sim units per real second)
        self.delta_sim = self.sim_speed * 0.05  # 50 ms per tick -> 0.05 real seconds
        self.running = False

    def start(self):
        self.running = True
        self.timer.start(50)  # 20 ticks per second (real time)

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

    def on_dispatch_pallet(self, data):
        pallet_id = data["id"]
        self.scene.toggle_payload_visibility(pallet_id, visible=True)

    def on_store_pallet(self, data):
        pallet_id = data["id"]
        self.scene.toggle_payload_visibility(pallet_id, visible=False)

    def on_move_payload(self, data):
        payload_id = data["id"]
        new_pos = data["coords"]
        self.scene.update_payload_position(payload_id, new_pos)

    def on_update_pallet_state(self, data):
        pallet_id = data["id"]
        new_state = data["state"]
        self.scene.update_pallet_state(pallet_id, new_state)
