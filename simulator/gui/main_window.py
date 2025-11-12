from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QToolBar, QSplitter, QLabel, QWidget, QSizePolicy, \
    QPushButton
from simulator.gui.factory_scene import FactoryScene
from simulator.gui.factory_view import FactoryView
from simulator.gui.simulation_controller import SimulationController
from simulator.gui.dialogs import SingleItemOrderDialog, MultiItemOrderDialog, LogDialog
from simulator.gui.dashboard import Dashboard
from simulator.core.factory.factory import Factory
import math

class MainWindow(QMainWindow):
    """

    """
    def __init__(self, factory: Factory, scene: FactoryScene, controller: SimulationController, db_manager):
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

        self.scene = scene
        self.view = FactoryView(self.scene)

        # Add QSpiller for factory and dashboard visualization
        self.dashboard = Dashboard(db_manager)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.dashboard)
        self.splitter.setSizes([int(screen_width * 0.6), int(screen_width * 0.4)])

        self.setCentralWidget(self.splitter)

        # Initialize dialogs once
        self.refill_order_dialog = SingleItemOrderDialog(factory.inventory_manager, self)
        self.refill_order_dialog.hide()

        self.opm_order_dialog = MultiItemOrderDialog(factory.inventory_manager, self)
        self.opm_order_dialog.hide()

        self.log_dialog = LogDialog(self)

        # Toolbar setup
        self._create_toolbar()

        # Connect the controller's time changed signal to the update method
        self.controller.time_changed.connect(self.update_simulation_time)
        self.controller.speed_changed.connect(self.update_speed_button_text)

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

        # Speed control button
        initial_speed = self.controller.speeds[self.controller.speed_index]
        self.speed_action = QAction(f"Speed: {initial_speed:.1f}x", self)
        self.speed_action.triggered.connect(self.controller.change_speed)
        toolbar.addAction(self.speed_action)

        # Simulation time label
        self.time_label = QLabel("Time: 0")
        self.time_label.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        toolbar.addWidget(self.time_label)

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

        # Spacer widget to push the dashboard button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Dashboard toggle button (as a QPushButton for easy styling)
        self.dashboard_button = QPushButton("Dashboard")
        self.dashboard_button.setCheckable(True)
        self.dashboard_button.setChecked(True)
        self.dashboard_button.toggled.connect(self.toggle_dashboard)
        toolbar.addWidget(self.dashboard_button)

    def update_simulation_time(self, time: int):
        """
        Slot to update the simulation time label.
        """
        self.time_label.setText(f"Time: {time}")

    def update_speed_button_text(self, speed: float):
        """Slot to update the speed control button's text."""
        self.speed_action.setText(f"Speed: {speed:.1f}x")

    def toggle_dashboard(self, checked: bool):
        """
        Shows or hides the dashboard widget based on the checkbox state.
        """
        self.dashboard.setVisible(checked)
