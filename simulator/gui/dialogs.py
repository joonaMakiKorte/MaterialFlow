from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QFrame, QGridLayout, QTextEdit, QTableWidget, QHeaderView, QTableWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from simulator.core.orders.inventory_manager import InventoryManager
from simulator.core.utils.logging_config import log_manager

class SingleItemOrderDialog(QDialog):
    def __init__(self, inventory_manager: InventoryManager, parent=None):
        super().__init__(parent)
        self.inventory_manager = inventory_manager
        self.setWindowTitle("Place Refill Order")
        self.setModal(False)  # allow interaction with main window
        self.setFixedSize(420, 340)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border-radius: 8px;
                color: #f0f0f0;
            }
            QLabel {
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox {
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #555;
                background-color: #3c3c3c;
                color: #f0f0f0;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QSpinBox {
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #555;
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
                color: #f0f0f0;
            }
            QPushButton#placeBtn {
                background-color: #0078d7;
            }
            QPushButton#placeBtn:hover {
                background-color: #005fa3;
            }
            QPushButton#closeBtn {
                background-color: #555;
            }
            QPushButton#closeBtn:hover {
                background-color: #666;
            }
        """)

        layout = QVBoxLayout(self)

        # --- Top section: item selector ---
        title = QLabel("Select item to order:")
        title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        self.item_combo = QComboBox()
        layout.addWidget(self.item_combo)
        self.item_combo.currentIndexChanged.connect(self.update_item_info)

        # --- Info section for selected item ---
        info_frame = QFrame()
        info_layout = QGridLayout(info_frame)
        info_layout.setContentsMargins(0, 10, 0, 10)
        info_layout.setHorizontalSpacing(10)
        info_layout.setVerticalSpacing(5)

        self.info_labels = {
            "id": QLabel("-"),
            "name": QLabel("-"),
            "category": QLabel("-"),
            "weight": QLabel("-"),
            "volume": QLabel("-"),
            "stackable": QLabel("-")
        }

        row = 0
        for label, widget in self.info_labels.items():
            info_layout.addWidget(QLabel(label.capitalize() + ":"), row, 0, Qt.AlignmentFlag.AlignRight)
            info_layout.addWidget(widget, row, 1)
            row += 1

        layout.addWidget(info_frame)

        # --- Quantity ---
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(1)
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.place_btn = QPushButton("Place")
        self.place_btn.setObjectName("placeBtn")
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        button_layout.addWidget(self.place_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.place_btn.clicked.connect(self._on_place_order)
        close_btn.clicked.connect(self.hide)

        # Track selected item (visible)
        self.selected_item: int | None = None

        # Initialize item list
        self.refresh_items()

    def refresh_items(self):
        """Refresh dropdown items."""
        self.item_combo.clear()
        all_items = self.inventory_manager.catalogue.items
        sorted_item_list = sorted(all_items, key=lambda item_tuple: item_tuple[1].name)

        for item_id, item in sorted_item_list:
            # Show name but store ID as userData
            display_name = f"{item.name} ({item.category})"
            self.item_combo.addItem(display_name, userData=item_id)

        # Update display to first item
        if self.item_combo.count() > 0:
            self.update_item_info(0)

    def update_item_info(self, index):
        """Update info panel based on selection."""
        item_id = self.item_combo.itemData(index)
        if item_id is None:
            return

        # Set as selected
        self.selected_item = item_id

        item = self.inventory_manager.catalogue[item_id]
        self.info_labels["id"].setText(str(item.item_id))
        self.info_labels["name"].setText(item.name)
        self.info_labels["category"].setText(item.category)
        self.info_labels["weight"].setText(f"{item.weight:.2f} kg")
        self.info_labels["volume"].setText(f"{item.volume:.2f} L")
        self.info_labels["stackable"].setText("Yes" if item.stackable else "No")

    def _on_place_order(self):
        item = self.selected_item
        quantity = self.quantity_spin.value()
        try:
            self.inventory_manager.place_refill_order(item, quantity)
            self.hide()
        except Exception as e:
            print(f"Failed to place order: {e}")

    def show_dialog(self):
        self.show()
        self.raise_()
        self.activateWindow()


class MultiItemOrderDialog(QDialog):
    def __init__(self, inventory_manager : InventoryManager, parent=None):
        super().__init__(parent)
        self.inventory_manager = inventory_manager
        self.setWindowTitle("Place OPM-order")
        self.setModal(False)
        self.setMinimumSize(550, 450)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border-radius: 8px;
                color: #f0f0f0;
            }
            QLabel {
                font-size: 13px;
                color: #e0e0e0;
            }
            QComboBox, QSpinBox {
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #555;
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                border: 1px solid #555;
                selection-background-color: #0078d7;
            }
            QTableWidget {
                background-color: #3c3c3c;
                border-radius: 6px;
                border: 1px solid #555;
                gridline-color: #555;
            }
            QHeaderView::section {
                background-color: #444;
                color: #f0f0f0;
                padding: 4px;
                border: 1px solid #555;
            }
            QPushButton {
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
                color: #f0f0f0;
            }
            QPushButton#addBtn {
                background-color: #28a745;
            }
            QPushButton#addBtn:hover {
                background-color: #218838;
            }
            QPushButton#deleteBtn {
                background-color: #dc3545;
            }
            QPushButton#deleteBtn:hover {
                background-color: #c82333;
            }
            QPushButton#placeBtn {
                background-color: #0078d7;
            }
            QPushButton#placeBtn:hover {
                background-color: #005fa3;
            }
            QPushButton#closeBtn {
                background-color: #555;
            }
            QPushButton#closeBtn:hover {
                background-color: #666;
            }
        """)

        layout = QVBoxLayout(self)

        # --- Item Selection ---
        selection_layout = QHBoxLayout()
        self.item_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        add_btn = QPushButton("Add Item")
        add_btn.setObjectName("addBtn")

        selection_layout.addWidget(QLabel("Item:"))
        selection_layout.addWidget(self.item_combo, 1)
        selection_layout.addWidget(QLabel("Quantity:"))
        selection_layout.addWidget(self.quantity_spin)
        selection_layout.addWidget(add_btn)
        layout.addLayout(selection_layout)

        # --- Order Table ---
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Item ID", "Name", "Quantity", "Action"])
        self.order_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.order_table)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.place_btn = QPushButton("Place Order")
        self.place_btn.setObjectName("placeBtn")
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        button_layout.addWidget(self.place_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        add_btn.clicked.connect(self._on_add_item)
        self.place_btn.clicked.connect(self._on_place_order)
        close_btn.clicked.connect(self.hide)

        # Initialize item list
        self.refresh_items()

    def refresh_items(self):
        """Refreshes the items in the combo box."""
        self.item_combo.clear()
        all_items = self.inventory_manager.catalogue.items
        sorted_item_list = sorted(all_items, key=lambda item_tuple: item_tuple[1].name)

        for item_id, item in sorted_item_list:
            # Show name but store ID as userData
            display_name = f"{item.name} ({item.category})"
            self.item_combo.addItem(display_name, userData=item_id)

    def _on_add_item(self):
        """Adds the selected item and quantity to the order table."""
        item_id = self.item_combo.currentData()
        if item_id is None:
            return

        item_name = self.item_combo.currentText().split(" (ID:")[0]
        quantity = self.quantity_spin.value()

        # Check if item is already in the table
        for row in range(self.order_table.rowCount()):
            if self.order_table.item(row, 0).text() == str(item_id):
                # Update quantity
                current_quantity = int(self.order_table.item(row, 2).text())
                self.order_table.setItem(row, 2, QTableWidgetItem(str(current_quantity + quantity)))
                return

        # Add new row
        row_position = self.order_table.rowCount()
        self.order_table.insertRow(row_position)
        self.order_table.setItem(row_position, 0, QTableWidgetItem(str(item_id)))
        self.order_table.setItem(row_position, 1, QTableWidgetItem(item_name))
        self.order_table.setItem(row_position, 2, QTableWidgetItem(str(quantity)))

        delete_btn = QPushButton("Remove")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self._on_delete_item)
        self.order_table.setCellWidget(row_position, 3, delete_btn)

    def _on_delete_item(self):
        """Removes the row corresponding to the clicked 'Remove' button."""
        clicked_button = self.sender()
        if clicked_button:
            # Find the row of the button that was clicked
            for row in range(self.order_table.rowCount()):
                if self.order_table.cellWidget(row, 3) == clicked_button:
                    self.order_table.removeRow(row)
                    break  # Stop searching once the row is found and removed

    def _on_place_order(self):
        """Gathers items and quantities and places the order."""
        if self.order_table.rowCount() == 0:
            print("No items in the order.")
            return

        items_to_order = {}
        for row in range(self.order_table.rowCount()):
            item_id = int(self.order_table.item(row, 0).text())
            quantity = int(self.order_table.item(row, 2).text())
            items_to_order[item_id] = quantity

        self.inventory_manager.place_opm_order(items_to_order)

        # Clear the table and close the dialog after placing the order
        self.order_table.setRowCount(0)
        self.accept()

    def show_dialog(self):
        self.show()
        self.raise_()
        self.activateWindow()


class LogDialog(QDialog):
    # Set the refresh rate for the log viewer in milliseconds
    REFRESH_INTERVAL_MS = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Log Viewer")
        self.setModal(False)
        self.setMinimumSize(800, 600)

        # Apply a consistent stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                 color: #f0f0f0; 
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #555;
                border-radius: 4px; 
            }
            QPushButton { 
                padding: 6px 14px;
                border-radius: 4px; 
                border: none; 
                color: #f0f0f0; 
                background-color: #555;
            }
            QPushButton:hover { 
                background-color: #666;
            }
            QComboBox { 
                padding: 4px; 
                border-radius: 4px; 
                border: 1px solid #555; 
                background-color: #3c3f41;
            }
            QLabel { 
                font-weight: bold; 
            }
        """)

        # --- Layouts and Widgets ---
        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Component:"))
        self.component_filter = QComboBox()
        self.component_filter.setMinimumWidth(300)
        self.component_filter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.component_filter.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.component_filter.currentTextChanged.connect(self._update_logs)  # Update when selection changes
        filter_layout.addWidget(self.component_filter)
        filter_layout.addStretch()  # Pushes the filter to the left
        layout.addLayout(filter_layout)

        # Main log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Monospace", 10))
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_display)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # --- Timer for live polling ---
        self.timer = QTimer(self)
        self.timer.setInterval(self.REFRESH_INTERVAL_MS)
        self.timer.timeout.connect(self._update_logs)

    def _update_component_filter(self):
        """Updates the dropdown with the latest list of component IDs."""
        current_selection = self.component_filter.currentText()
        all_ids = log_manager.get_unique_component_ids()

        # Block signals to prevent this update from triggering a log refresh
        self.component_filter.blockSignals(True)

        # Rebuild the list
        self.component_filter.clear()
        self.component_filter.addItem("All Logs")
        self.component_filter.addItems(all_ids)

        # Restore previous selection if it still exists
        index = self.component_filter.findText(current_selection)
        if index != -1:
            self.component_filter.setCurrentIndex(index)

        self.component_filter.blockSignals(False)

    def _update_logs(self):
        """Fetches and displays logs based on the current filter."""
        # First, ensure the component list is up-to-date
        self._update_component_filter()

        selected_component = self.component_filter.currentText()

        # Check if the user is scrolled to the bottom before we update
        scrollbar = self.log_display.verticalScrollBar()
        is_at_bottom = scrollbar.value() >= scrollbar.maximum() - 5

        # Fetch logs based on filter
        if selected_component == "All Logs":
            logs = log_manager.get_all_logs()
        else:
            logs = log_manager.get_component_logs(selected_component)

        log_text = "\n".join(logs)
        self.log_display.setText(log_text)

        # Auto-scroll only if the user was already at the bottom
        if is_at_bottom:
            scrollbar.setValue(scrollbar.maximum())

    def showEvent(self, event):
        """Called when the dialog is shown."""
        super().showEvent(event)
        # Populate immediately and start the timer
        self._update_logs()
        self.timer.start()

    def hideEvent(self, event):
        """Called when the dialog is hidden or closed."""
        super().hideEvent(event)
        # Stop the timer to save resources
        self.timer.stop()