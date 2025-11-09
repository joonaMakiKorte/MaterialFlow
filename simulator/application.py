from simulator.core.factory.factory import Factory
from simulator.core.utils.event_bus import EventBus
from simulator.database.database_listener import DatabaseListener
from simulator.database.database_manager import DatabaseManager
import simpy
from simulator.gui.main_window import MainWindow
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.simulation_controller import SimulationController

class Application:
    """
    The Composition Root of the application.
    Owns all major components and wires them together.
    """
    def __init__(self):
        # Initialize core, independent services
        self.event_bus = EventBus()
        self.env = simpy.Environment()

        # Create and setup data persistence
        self.db_manager = DatabaseManager()
        self.db_manager.setup_database()

        # Create the components and inject their dependencies
        self.db_listener = DatabaseListener(self.event_bus, self.db_manager)
        self.factory = Factory(self.env, self.event_bus)
        self.scene = FactoryScene(self.factory)
        self.controller = SimulationController(self.env, self.scene)
        self.window = MainWindow(self.factory, self.scene, self.controller, self.db_manager)

    def run(self):
        """
        Starts the application logic after setup.
        """
        self.db_listener.setup_subscriptions()
        self.controller.setup_subscriptions()
        self.factory.init_simulation()

        # Show the UI and start the event loop
        self.window.show()
