from simulator.core.factory.factory import Factory
from simulator.core.utils.event_bus import EventBus
from simulator.database.database_listener import DatabaseListener
from simulator.database.database_manager import DatabaseManager
import simpy
from simulator.gui.main_window import MainWindow
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.simulation_controller import SimulationController
import logging
logger = logging.getLogger(__name__)

class Application:
    """
    The Composition Root of the application.
    Owns all major components and wires them together.
    """
    def __init__(self):
        # Initialize core, independent services
        logger.info("Initializing core services...")
        self.event_bus = EventBus()
        self.env = simpy.Environment()

        # Create and setup data persistence
        logger.info("Setting up database schema...")
        self.db_manager = DatabaseManager()
        self.db_manager.setup_database(fresh_start=True)
        self.db_listener = DatabaseListener(self.event_bus, self.db_manager)
        self.db_listener.setup_subscriptions()

        # Initialize simulation state
        logger.info("Initializing simulation state...")
        self.factory = Factory(self.env, self.event_bus)
        self.factory.init_simulation()

        logger.info("Database is now seeded with initial simulation data.")

        # Initialize the user interface
        logger.info("Initializing user interface...")
        self.scene = FactoryScene(self.factory)
        self.controller = SimulationController(self.env, self.scene)
        self.controller.setup_subscriptions()
        self.window = MainWindow(self.factory, self.scene, self.controller, self.db_manager)

    def run(self):
        """
        Starts the application logic after setup.
        """
        logger.info("Showing main window and starting application.")
        self.window.show()
