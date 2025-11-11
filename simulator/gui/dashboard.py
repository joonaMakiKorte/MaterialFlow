from PyQt6.QtWidgets import QHBoxLayout, QTabWidget
from simulator.gui.widgets import OrderQueryWidget, PalletQueryWidget, ChartsWidget
from simulator.database.database_manager import DatabaseManager
from PyQt6.QtWidgets import QWidget


class Dashboard(QWidget):
    """
    A container widget for the analytics dashboard, featuring a navigation
    menu and multiple pages for different data views.
    """

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)

        # Create widget and add tabs
        self.tabs = QTabWidget()
        order_page = OrderQueryWidget(self.db_manager)
        pallet_page = PalletQueryWidget(self.db_manager)
        charts_page = ChartsWidget(self.db_manager)

        self.tabs.addTab(order_page, "Orders")
        self.tabs.addTab(pallet_page, "Pallets")
        self.tabs.addTab(charts_page, "Charts")

        main_layout.addWidget(self.tabs, stretch=1)