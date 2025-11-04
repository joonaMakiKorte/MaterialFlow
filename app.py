from PyQt6.QtWidgets import QApplication
from simulator.core.factory.factory import Factory
from simulator.core.utils.event_bus import EventBus
from simulator.database.database_listener import DatabaseListener
import sys
import simpy
from simulator.gui.main_window import MainWindow
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.simulation_controller import SimulationController


def main():
    # Initialize app
    app = QApplication(sys.argv)

    # Initialize core components
    env = simpy.Environment()
    event_bus = EventBus()

    # Initialize simulation
    factory = Factory(env, event_bus)
    factory.init_simulation()

    # Setup database
    db_listener = DatabaseListener(event_bus)
    db_listener.setup_subscriptions()

    # Create scene and simulation controller
    scene = FactoryScene(factory)
    controller = SimulationController(env, scene)

    # Create and show main window
    window = MainWindow(factory, scene, controller)
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()