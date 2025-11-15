from PyQt6.QtCore import QAbstractTableModel, Qt
from simulator.database.models import Order, Item, Pallet

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

class PalletTableModel(QAbstractTableModel):
    """
    A custom model to display a list of Pallet objects in a QTableView.
    """

    def __init__(self, data: list[Pallet]):
        super().__init__()
        self._data = data
        self._headers = [
            "ID", "Location", "Destination", "Order ID", "Last Updated Time"
        ]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        pallet = self._data[index.row()]
        column = index.column()

        if column == 0:
            return pallet.id
        elif column == 1:
            return pallet.location if pallet.location is not None else "N/A"
        elif column == 2:
            return pallet.destination if pallet.destination is not None else "N/A"
        elif column == 3:
            return pallet.order_id if pallet.order_id is not None else "N/A"
        elif column == 4:
            return f"{pallet.last_updated_sim_time:.2f}"

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def set_data(self, data: list[Pallet]):
        """Updates the model's data and refreshes the view."""
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class ItemTableModel(QAbstractTableModel):
    """
    A custom model to display a list of Item objects in a QTableView.
    """

    def __init__(self, data: list[Item]):
        super().__init__()
        self._data = data
        self._headers = ["Item ID", "Name", "Weight (kg)", "Category", "Volume (L)", "Stackable"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        item = self._data[index.row()]
        column = index.column()

        if column == 0:
            return item.id
        elif column == 1:
            return item.name
        elif column == 2:
            return f"{item.weight:.2f}"
        elif column == 3:
            return item.category
        elif column == 4:
            return f"{item.volume:.2f}"
        elif column == 5:
            return "Yes" if item.stackable else "No"

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def set_data(self, data: list[Item]):
        """Resets the model with new data."""
        self.beginResetModel()
        self._data = data
        self.endResetModel()