from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QApplication, QToolBar
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.simulation_controller import SimulationController
from simulator.gui.dialogs import SingleItemOrderDialog, MultiItemOrderDialog, LogDialog
from simulator.core.factory.factory import Factory
import math

class MainWindow(QMainWindow):
    """

    """
    def __init__(self, factory: Factory, scene: FactoryScene, controller: SimulationController):
        super().__init__()
        self.setWindowTitle("Material Flow")
        self.controller = controller

        # Window sizing and centering
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        screen_width = math.ceil(available_geometry.width() * 0.9)
        screen_height = math.ceil(available_geometry.height() * 0.9)
        self.resize(screen_width, screen_height)

        frame_geom = self.frameGeometry()
        center_point = available_geometry.center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())

        # Factory scene and view setup
        self.view = QGraphicsView()
        self.scene = scene
        self.scene.scale_scene(screen_width, screen_height)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Initialize dialogs once
        self.refill_order_dialog = SingleItemOrderDialog(factory.inventory_manager, self)
        self.refill_order_dialog.hide()

        self.opm_order_dialog = MultiItemOrderDialog(factory.inventory_manager, self)
        self.opm_order_dialog.hide()

        self.log_dialog = LogDialog(self)

        # Toolbar setup
        self._create_toolbar()

    def _create_toolbar(self):
        toolbar = QToolBar("Simulation Controls")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setStyleSheet("QToolBar { spacing: 10px; }")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # Run button
        run_action = QAction(QIcon.fromTheme("media-playback-start"), "Run", self)
        run_action.triggered.connect(self.controller.start)
        toolbar.addAction(run_action)

        # Pause button
        pause_action = QAction(QIcon.fromTheme("media-playback-pause"), "Pause", self)
        pause_action.triggered.connect(self.controller.stop)
        toolbar.addAction(pause_action)

        toolbar.addSeparator()

        # Place RefillOrder button
        refill_order_action = QAction("Refill Order", self)
        refill_order_action.triggered.connect(self.refill_order_dialog.show_dialog)
        toolbar.addAction(refill_order_action)

        # Place OpmOrder button
        opm_order_action = QAction("OPM Order", self)
        opm_order_action.triggered.connect(self.opm_order_dialog.show_dialog)
        toolbar.addAction(opm_order_action)

        # View Log button
        log_action = QAction("View Log", self)
        log_action.triggered.connect(self.log_dialog.show)
        toolbar.addAction(log_action)
