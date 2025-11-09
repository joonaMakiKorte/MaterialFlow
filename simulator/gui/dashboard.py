from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout,
                             QTableView, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont



class Dashboard(QWidget):
    """
    A widget that displays analytics and KPIs by querying the database.
    (PyQt6 Version)
    """
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager

        self.setWindowTitle("Analytics Dashboard")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Title ---
        title_label = QLabel("Analytics Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        # In PyQt6, enums are fully qualified. Qt.AlignCenter is now Qt.AlignmentFlag.AlignCenter
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Refresh Button ---
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_all_data)
        main_layout.addWidget(self.refresh_button)

        # --- KPI Section ---
        kpi_frame = QFrame()
        # The QFrame.Shape enum is used here
        kpi_frame.setFrameShape(QFrame.Shape.StyledPanel)
        kpi_layout = QGridLayout(kpi_frame)

        # Create labels for KPIs (title and value)
        self.kpi_total_orders_val = self._create_kpi_label("N/A")
        self.kpi_completed_orders_val = self._create_kpi_label("N/A")
        self.kpi_avg_time_val = self._create_kpi_label("N/A")

        kpi_layout.addWidget(QLabel("Total Orders:"), 0, 0)
        kpi_layout.addWidget(self.kpi_total_orders_val, 0, 1)
        kpi_layout.addWidget(QLabel("Completed Orders:"), 1, 0)
        kpi_layout.addWidget(self.kpi_completed_orders_val, 1, 1)
        kpi_layout.addWidget(QLabel("Avg. Completion Time:"), 2, 0)
        kpi_layout.addWidget(self.kpi_avg_time_val, 2, 1)

        main_layout.addWidget(kpi_frame)

        # --- Chart Placeholder ---
        chart_placeholder = QWidget()
        # The QSizePolicy.Policy enum is used here
        chart_placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chart_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        chart_label = QLabel("Chart Placeholder (e.g., for Matplotlib/PyQtGraph)")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_layout = QVBoxLayout(chart_placeholder)
        chart_layout.addWidget(chart_label)
        main_layout.addWidget(chart_placeholder)

        # --- Table View ---
        self.order_table = QTableView()
        main_layout.addWidget(self.order_table)

    def _create_kpi_label(self, text):
        """Helper to create a styled label for KPI values."""
        label = QLabel(text)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        return label

    def refresh_all_data(self):
        """Placeholder function to query the DB and update the UI."""
        print("DASHBOARD: Refreshing data...")

        # This dummy data logic is pure Python and needs no changes
        import random
        total_orders = random.randint(50, 100)
        completed_orders = random.randint(10, total_orders)
        avg_time = round(random.uniform(200, 500), 2)

        self.kpi_total_orders_val.setText(str(total_orders))
        self.kpi_completed_orders_val.setText(str(completed_orders))
        self.kpi_avg_time_val.setText(f"{avg_time} s")