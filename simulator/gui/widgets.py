from PyQt6.QtCore import Qt
from simulator.gui.table_models import OrderTableModel, ItemTableModel
from simulator.database.database_manager import DatabaseManager
from simulator.database.models import OrderStatus, Order, RefillOrder, OpmOrder
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QTableView, QGroupBox, QFormLayout,
                             QComboBox, QLineEdit, QHeaderView, QLabel, QTextEdit, QGridLayout)

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

        self.status_combo.addItem("All", None)
        for status in OrderStatus:
            self.status_combo.addItem(status.name, status)

        self.type_combo.addItem("All", None)
        self.type_combo.addItem("RefillOrder", "RefillOrder")
        self.type_combo.addItem("OpmOrder", "OpmOrder")

        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Type:", self.type_combo)

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


class ItemQueryWidget(QWidget):
    """
    A widget to display and filter the factory's item catalogue.
    """

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._init_ui()
        # Load all data initially
        self._on_search_clicked()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Filter Panel
        filter_groupbox = QGroupBox("Filter Criteria")
        form_layout = QFormLayout(filter_groupbox)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Widget")

        self.category_combo = QComboBox()

        self.stackable_combo = QComboBox()
        self.stackable_combo.addItem("All", None)  # Text, UserData
        self.stackable_combo.addItem("Yes", True)
        self.stackable_combo.addItem("No", False)

        form_layout.addRow("Name Contains:", self.name_input)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Stackable:", self.stackable_combo)

        main_layout.addWidget(filter_groupbox)

        self.search_button = QPushButton("Search Items")
        self.search_button.clicked.connect(self._on_search_clicked)
        main_layout.addWidget(self.search_button)

        self.item_table = QTableView()
        self.table_model = ItemTableModel([])  # Assumes ItemTableModel is defined
        self.item_table.setModel(self.table_model)

        self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.item_table.setSortingEnabled(True)

        main_layout.addWidget(self.item_table)

        # Populate dynamic filters after UI is created
        self._populate_category_filter()

    def _populate_category_filter(self):
        """Fetches all unique item categories and populates the dropdown."""
        self.category_combo.clear()
        self.category_combo.addItem("All", None)
        categories = self.db_manager.get_all_item_categories()
        for category in categories:
            self.category_combo.addItem(category, category)

    def _on_search_clicked(self):
        """Gathers filter criteria, queries the database, and updates the table."""
        kwargs = {}

        name_text = self.name_input.text().strip()
        if name_text:
            kwargs['name_contains'] = name_text

        category = self.category_combo.currentData()
        if category is not None:
            kwargs['category'] = category

        stackable = self.stackable_combo.currentData()
        if stackable is not None:
            kwargs['stackable'] = stackable

        items = self.db_manager.query_items(**kwargs)
        self.table_model.set_data(items)

class ChartsWidget(QWidget):
    """Placeholder for the Charts view."""
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        label = QLabel("Charts & KPIs Dashboard - Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)


class SearchWidget(QWidget):
    """
    A widget to find and display details for a specific entity
    (Order, Pallet, or Item) by its unique ID.
    """

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding

        # --- Search Input Group ---
        search_groupbox = QGroupBox("Find Entity by ID")
        search_layout = QGridLayout(search_groupbox)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter numeric ID for an Order, Pallet, or Item")

        self.find_button = QPushButton("Find")
        self.find_button.clicked.connect(self._on_find_clicked)

        search_layout.addWidget(QLabel("Entity ID:"), 0, 0)
        search_layout.addWidget(self.id_input, 0, 1)
        search_layout.addWidget(self.find_button, 0, 2)

        main_layout.addWidget(search_groupbox)

        # --- Details Display Area ---
        details_groupbox = QGroupBox("Details")
        details_layout = QVBoxLayout(details_groupbox)

        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setPlaceholderText(
            "Enter an ID above and click 'Find' to see details.\n\n"
            "The system will determine if the ID belongs to an Order, Pallet, or Item."
        )

        details_layout.addWidget(self.details_display)
        main_layout.addWidget(details_groupbox, stretch=1)  # Give display area extra space

    def _on_find_clicked(self):
        """
        Placeholder for the search logic.
        """
        entity_id_text = self.id_input.text().strip()
        if not entity_id_text:
            self.details_display.setText("Please enter an ID.")
            return

        # --- LOGIC TO BE IMPLEMENTED LATER ---
        # 1. Validate that entity_id_text is an integer.
        # 2. Query the database for an Order with this ID.
        # 3. If not found, query for a Pallet with this ID.
        # 4. If not found, query for an Item with this ID.
        # 5. If found, call a helper method to format and display the details.
        # 6. If not found in any table, display a "Not Found" message.

        # For now, just show a placeholder message.
        self.details_display.setText(f"Search logic for ID '{entity_id_text}' is not yet implemented.")
