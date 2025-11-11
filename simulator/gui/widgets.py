from PyQt6.QtCore import Qt
from simulator.gui.table_models import OrderTableModel
from simulator.database.database_manager import DatabaseManager
from simulator.database.models import OrderStatus
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QTableView, QGroupBox, QFormLayout,
                             QComboBox, QLineEdit, QHeaderView, QLabel)

class OrderQueryWidget(QWidget):
    """
    A self-contained widget for filtering and displaying orders.
    """

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Filter panel
        filter_groupbox = QGroupBox("Filter Criteria")
        form_layout = QFormLayout(filter_groupbox)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.status_combo = QComboBox()
        self.type_combo = QComboBox()
        self.item_id_input = QLineEdit()
        self.limit_input = QLineEdit()

        self.status_combo.addItem("All", None)
        for status in OrderStatus:
            self.status_combo.addItem(status.name, status)

        self.type_combo.addItem("All", None)
        self.type_combo.addItem("RefillOrder", "RefillOrder")
        self.type_combo.addItem("OpmOrder", "OpmOrder")

        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Type:", self.type_combo)
        form_layout.addRow("Item ID (Refill Only):", self.item_id_input)
        form_layout.addRow("Limit Results:", self.limit_input)

        main_layout.addWidget(filter_groupbox)

        self.search_button = QPushButton("Search Orders")
        self.search_button.clicked.connect(self._on_search_clicked)
        main_layout.addWidget(self.search_button)

        # Results table
        self.order_table = QTableView()
        self.table_model = OrderTableModel([])
        self.order_table.setModel(self.table_model)

        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table.setAlternatingRowColors(True)

        main_layout.addWidget(self.order_table, stretch=1)

    def _on_search_clicked(self):
        kwargs = {}
        status = self.status_combo.currentData()
        if status: kwargs['status'] = status
        order_type = self.type_combo.currentData()
        if order_type: kwargs['type'] = order_type

        item_id_text = self.item_id_input.text().strip()
        if item_id_text:
            try:
                kwargs['item_id'] = int(item_id_text)
            except ValueError:
                pass

        limit_text = self.limit_input.text().strip()
        if limit_text:
            try:
                kwargs['limit'] = int(limit_text)
            except ValueError:
                pass

        kwargs['order_by'] = '-order_time'

        results = self.db_manager.query_orders(**kwargs)
        self.table_model.set_data(results)

class PalletQueryWidget(QWidget):
    """Placeholder for the Pallet query view."""
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        label = QLabel("Pallet Table View - Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

class ChartsWidget(QWidget):
    """Placeholder for the Charts view."""
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        label = QLabel("Charts & KPIs Dashboard - Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)