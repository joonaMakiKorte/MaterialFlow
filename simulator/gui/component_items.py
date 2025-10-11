from enum import Enum
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import QRectF, Qt, QPointF
from simulator.config import PALLET_ITEM_WIDTH, BUFFER_ITEM_WIDTH, DEPALLETIZER_ITEM_WIDTH, BATCH_ITEM_WIDTH

class BaseItem(QGraphicsItem):
    """
    Base model for a component item. Each component is essentially a rectangle.
    A single coordinate in the factory covers 100x100 graphical coordinate space.
    For factory components z value is 0 and for transportation units z is 10, so that
    payloads get modelled on top of components.
    """
    def __init__(self, x, y, rect, color, z=0):
        super().__init__()
        self.rect = rect
        self.color = QColor(color)
        self.setPos(100*x, 100*y)
        self.setZValue(z)

    def boundingRect(self):
        return self.rect

# -------------------------
# Transportation unit items
# -------------------------

class PalletState(Enum):
    EMPTY = 0
    REFILL_ORDER = 1
    OPM_ORDER = 2

class PalletItem(BaseItem):
    """
    Pallets are modelled as 60x60 rectangles.
    Color is determined by pallet state (empty or carrying an order).
    When in storage, pallets are not rendered.
    """
    def __init__(self, coordinate=(0,0), state=PalletState.EMPTY, visible=False):
        self.state = state
        self.visible = visible

        rect = QRectF(
            -PALLET_ITEM_WIDTH/2,
            -PALLET_ITEM_WIDTH/2,
            PALLET_ITEM_WIDTH,
            PALLET_ITEM_WIDTH)
        super().__init__(coordinate[0], coordinate[1], rect, color="gray", z=1)

    def paint(self, painter, option, widget=None):
        if not self.visible:
            return
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawRect(self.rect)

    def set_state(self, state: PalletState):
        """Update the pallet's state and refresh its color."""
        self.state = state
        self.update_color()
        self.update()

    def update_color(self):
        """Set color according to the current state."""
        if self.state == PalletState.EMPTY:
            self.color = QColor("gray")
        elif self.state == PalletState.REFILL_ORDER:
            self.color = QColor("cornflowerblue")
        elif self.state == PalletState.OPM_ORDER:
            self.color = QColor("orange")

    def show_pallet(self):
        """Make pallet visible."""
        self.visible = True
        self.update()

    def hide_pallet(self):
        """Make pallet invisible."""
        self.visible = False
        self.update()

    def update_position(self, coords: tuple[int,int]):
        """Update the position of pallet."""
        new_pos = QPointF(100 * coords[0], 100 * coords[1])
        self.setPos(new_pos)
        self.update()

class BatchState(Enum):
    IN_PROGRESS = 0
    READY = 1

class BatchItem(BaseItem):
    """
    A 50x50 rectangle that has 2 states: in progress (building) and ready.
    Are created inside batch builders and instance is alive only for the duration of transportation.
    """
    def __init__(self, coordinate: tuple[int, int], state=BatchState.IN_PROGRESS):
        self.state = state

        rect = QRectF(
            -BATCH_ITEM_WIDTH / 2,
            -BATCH_ITEM_WIDTH / 2,
            BATCH_ITEM_WIDTH,
            BATCH_ITEM_WIDTH)
        super().__init__(coordinate[0], coordinate[1], rect, color="cyan", z=1)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen())
        painter.drawRect(self.rect)


# ----------------
# Component items
# ----------------

class PayloadBufferItem(BaseItem):
    """
    Buffers are green 80x80 rectangles centered around (0,0).
    Essentially a single slot box
    """
    def __init__(self, coordinate: tuple[int, int]):
        rect = QRectF(
            -BUFFER_ITEM_WIDTH / 2,
            -BUFFER_ITEM_WIDTH / 2,
            BUFFER_ITEM_WIDTH,
            BUFFER_ITEM_WIDTH)
        super().__init__(coordinate[0], coordinate[1], rect, color="green")

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen())
        painter.drawRect(self.rect)


class PayloadConveyorItem(BaseItem):
    """
    A long rectangle divided into slots.
    A single conveyor slot is 80x80, but for visualizing purposes the slots in the middle merge together
    """
    def __init__(self, start: tuple[int,int], end: tuple[int,int]):
        self.start = start
        self.end = end
        self.num_slots = max(abs(start[0]-end[0]), abs(start[1]-end[1])) + 1

        # Determine width and height assuming the conveyor is along x-axis, else flip around
        width = (self.num_slots - 2) * 100 + 180
        height = 80
        self.is_vertical = False
        if start[0] == end[0]:  # vertical conveyor
            width, height = height, width
            self.is_vertical = True

        # Rotate (decide anchor corner based on direction)
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        x = start[0]
        y = start[1]
        if dx < 0 or dy < 0:  # Operation direction: right->left || down->up
            x, y = end[0], end[1]

        rect = QRectF(
            -BUFFER_ITEM_WIDTH/2,
            -BUFFER_ITEM_WIDTH/2,
            width,
            height)
        super().__init__(x, y, rect, color="lightgreen")

    def paint(self, painter, option, widget=None):
        # draw conveyor body
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor("darkgreen"), 2))
        painter.drawRect(self.rect)

        # draw slots
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("black"), 1, ))  # slot grid lines

        if self.is_vertical:
            for i in range(self.num_slots):
                top = -BUFFER_ITEM_WIDTH/2 + i*100
                # middle slots overlap, so reduce spacing after first and last
                if i == 0:
                    rect = QRectF(
                        -BUFFER_ITEM_WIDTH/2,
                        -BUFFER_ITEM_WIDTH/2,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                elif i == self.num_slots-1:
                    rect = QRectF(
                        -BUFFER_ITEM_WIDTH/2,
                        self.rect.height()-(BUFFER_ITEM_WIDTH/2)-BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                else:
                    rect = QRectF(
                        -BUFFER_ITEM_WIDTH/2,
                        top,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                painter.drawRect(rect)
        else:
            for i in range(self.num_slots):
                left = -BUFFER_ITEM_WIDTH/2 + i*100
                if i == 0:
                    rect = QRectF(
                        -BUFFER_ITEM_WIDTH/2,
                        -BUFFER_ITEM_WIDTH/2,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                elif i == self.num_slots-1:
                    rect = QRectF(
                        self.rect.width()-(BUFFER_ITEM_WIDTH/2)-BUFFER_ITEM_WIDTH,
                        -BUFFER_ITEM_WIDTH/2,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                else:
                    rect = QRectF(
                        left,
                        -BUFFER_ITEM_WIDTH/2,
                        BUFFER_ITEM_WIDTH,
                        BUFFER_ITEM_WIDTH)
                painter.drawRect(rect)


class DepalletizerItem(BaseItem):
    """
    A 100x100 rectangle that changes color when operating.
    Contains an internal 80x80 buffer
    """
    def __init__(self, coordinate: tuple[int, int]):
        rect = QRectF(
            -DEPALLETIZER_ITEM_WIDTH/2,
            -DEPALLETIZER_ITEM_WIDTH/2,
            DEPALLETIZER_ITEM_WIDTH,
            DEPALLETIZER_ITEM_WIDTH)
        super().__init__(coordinate[0], coordinate[1], rect, color="#AAAAAA")

        self.buffer_rect = QRectF(
            self.rect.x() + 10, # 10px margin all around
            self.rect.y() + 10,
            BUFFER_ITEM_WIDTH,
            BUFFER_ITEM_WIDTH
        )

        # State
        self.operating = False

    def on_operating(self, payload):
        """Called when the depalletizer starts working."""
        if payload.get("id") == id(self):  # or match your own depalletizer id
            self.operating = True
            self.color = QColor("#4CAF50")  # green
            self.update()

    def on_idle(self, payload):
        """Called when the depalletizer stops."""
        if payload.get("id") == id(self):
            self.operating = False
            self.color = QColor("#AAAAAA")  # back to gray
            self.update()

    def paint(self, painter, option, widget=None):
        # Draw the outer 100x100 depalletizer
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor("black")))
        painter.drawRect(self.rect)

        # Draw the internal 80x80 buffer slot
        painter.setBrush(QBrush(QColor("#CCCCCC")))
        painter.setPen(QPen(QColor("black")))
        painter.drawRect(self.buffer_rect)


class BatchBuilderItem(BaseItem):
    """
    A Batch Builder is similar to a PayloadBuffer but builds batches
    from depalletized items. It visually looks like an 80x80 block
    with two states: idle or building.
    """
    def __init__(self, coordinate: tuple[int, int]):
        rect = QRectF(
            -BUFFER_ITEM_WIDTH/2,
            -BUFFER_ITEM_WIDTH/2,
            BUFFER_ITEM_WIDTH,
            BUFFER_ITEM_WIDTH)
        super().__init__(coordinate[0], coordinate[1], rect, color="#808080") # default: idle gray

        self.operating = False

        # Make distinguishable from buffer
        self.border_color = QColor("black")
        self.border_thickness = 2

        # Subscribe to events
        #self.event_bus.subscribe("batch_builder_building", self.on_building)
        #self.event_bus.subscribe("batch_builder_idle", self.on_idle)

    def on_building(self, payload):
        """Switch to 'building' mode (active)."""
        if payload.get("id") == id(self):
            self.operating = True
            self.color = QColor("#FFA500")  # orange = building
            self.update()

    def on_idle(self, payload):
        """Switch back to 'idle' mode."""
        if payload.get("id") == id(self):
            self.operating = False
            self.color = QColor("#808080")  # gray = idle
            self.update()

    def paint(self, painter, option, widget=None):
        # Fill
        painter.setBrush(QBrush(self.color))
        pen = QPen(self.border_color)
        pen.setWidth(self.border_thickness)
        painter.setPen(pen)
        painter.drawRect(self.rect)