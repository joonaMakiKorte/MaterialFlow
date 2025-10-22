from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QFrame, QGridLayout, QTextEdit
)
from PyQt6.QtCore import Qt
from simulator.core.factory.factory import Factory

class OrderDialog(QDialog):
    def __init__(self, factory: Factory, parent=None):
        super().__init__(parent)
        self.factory = factory
        self.setWindowTitle("Place Order")
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
        for item_id, item in self.factory.catalogue.items:
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

        item = self.factory.catalogue[item_id]
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
            self.factory.inventory_manager.place_refill_order(item, quantity)
            self.hide()
        except Exception as e:
            print(f"Failed to place order: {e}")

    def show_order_dialog(self):
        self.show()
        self.raise_()
        self.activateWindow()


class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer") # A generic default title
        self.setModal(False)  # Allow interaction with the main window
        self.setMinimumSize(800, 600)

        # Apply a stylesheet similar to OrderDialog for a consistent look
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 5px;
            }
            QPushButton {
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
                color: #f0f0f0;
                background-color: #555;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

        layout = QVBoxLayout(self)

        # The main text area for displaying logs
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Monospace", 10)) # Monospaced font for clean log alignment
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Prevent wrapping for long lines
        layout.addWidget(self.log_display)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def show_logs(self, recent_logs: list[str], title: str):
        """
        Populates the dialog with logs from a given provider and shows it.

        Args:
            log_provider: Any object with a get_recent_logs() method that returns a list of strings.
            title: The title to set for the dialog window.
        """
        self.setWindowTitle(title)

        try:
            # Get the logs
            log_text = "\n".join(recent_logs)
            self.log_display.setText(log_text)

            # Automatically scroll to the bottom to show the most recent logs
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        except Exception as e:
            self.log_display.setText(f"Error: Could not retrieve logs.\n\n{e}")

        # Show the dialog
        self.show()
        self.raise_()
        self.activateWindow()