from PyQt6.QtCore import QAbstractTableModel, Qt
from simulator.database.models import Order

class OrderTableModel(QAbstractTableModel):
    """
    A custom model to display a list of Order objects in a QTableView.
    """

    def __init__(self, data: list[Order]):
        super().__init__()
        self._data = data
        self._headers = ["Order ID", "Type", "Status", "Order Time", "Completion Time"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        order = self._data[index.row()]
        column = index.column()

        if column == 0:
            return order.id
        elif column == 1:
            return order.type
        elif column == 2:
            # Display the enum member's name
            return order.status.name
        elif column == 3:
            return f"{order.order_time:.2f}"
        elif column == 4:
            return f"{order.completion_time:.2f}" if order.completion_time is not None else "N/A"

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def set_data(self, data: list[Order]):
        """Resets the model with new data."""
        self.beginResetModel()
        self._data = data
        self.endResetModel()
