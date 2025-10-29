from enum import Enum
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygonF, QFont, QFontMetrics
from PyQt6.QtCore import QRectF, Qt, QPointF
from simulator.gui.event_bus import EventBus
from abc import abstractmethod

# -------------
# Payload items
# -------------

class BasePayloadItem(QGraphicsItem):
    def __init__(self, state, rect, color, z=10):
        super().__init__()
        self.state = state
        self.rect = rect    # Active rect used for drawing
        self.color = QColor(color)
        self.setZValue(z)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawRect(self.rect)

    def update_position(self, x: float, y: float):
        new_pos = QPointF(x, y)
        self.setPos(new_pos)
        self.update()

    def set_state(self, state):
        self.state = state
        self.update_color()
        self.update()

    @abstractmethod
    def update_color(self):
        pass


class PalletState(Enum):
    EMPTY = 0
    REFILL_ORDER = 1
    OPM_ORDER = 2

# Registry for connecting pallet states to gui representations
PALLET_ORDER_STATES = {
    "Empty" : PalletState.EMPTY,
    "RefillOrder" : PalletState.REFILL_ORDER,
    "OpmOrder" : PalletState.OPM_ORDER
}

class PalletItem(BasePayloadItem):
    """
    Pallets are modelled as 60x60 rectangles.
    Color is determined by pallet state (empty or carrying an order).
    When in storage, pallets are not rendered.
    """
    def __init__(self, state=PalletState.EMPTY):
        rect = QRectF(-30,-30,60,60)
        super().__init__(state, rect, color="gray")

    def update_color(self):
        """Set color according to the current state."""
        if self.state == PalletState.EMPTY:
            self.color = QColor("gray")
        elif self.state == PalletState.REFILL_ORDER:
            self.color = QColor("cornflowerblue")
        elif self.state == PalletState.OPM_ORDER:
            self.color = QColor("orange")


class BatchState(Enum):
    BUILDING = 0
    READY = 1

class BatchItem(BasePayloadItem):
    """
    A 50x50 rectangle that has 2 states: in progress (building) and ready.
    Are created inside batch builders and instance is alive only for the duration of transportation.
    """
    def __init__(self, state=BatchState.BUILDING):
        rect = QRectF(-25,-25,50,50)
        super().__init__(state, rect, color="cyan")

    def update_color(self):
        """Set color according to the current state."""
        if self.state == BatchState.BUILDING:
            self.color = QColor("cyan")
        elif self.state == BatchState.READY:
            self.color = QColor("magenta")


# ----------------
# Component items
# ----------------

class BaseComponentItem(QGraphicsItem):
    """
    Base model for a component item.
    Stores event bus for event handling.
    """
    def __init__(self, component_id: str, x: float, y: float, event_bus: EventBus, rect: QRectF, color, z=0):
        super().__init__()
        self.id = component_id
        self.x = x
        self.y = y
        self.event_bus = event_bus
        self.rect = rect  # Active rect used for drawing
        self.color = QColor(color)
        self.setZValue(z)

    def boundingRect(self):
        return self.rect

class PayloadBufferItem(BaseComponentItem):
    """
    Buffers are green 80x80 rectangles centered around (0,0).
    Essentially a single slot box
    """
    def __init__(self, component_id: str, coordinate: tuple[int, int], event_bus: EventBus):
        rect = QRectF(-40,-40,80,80)
        super().__init__(component_id, coordinate[0], coordinate[1], event_bus, rect, color="green")

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen())
        painter.drawRect(self.rect)


class PayloadConveyorItem(BaseComponentItem):
    """
    A long rectangle divided into slots.
    A single conveyor slot is 80x80, but for visualizing purposes the slots in the middle merge together
    """
    def __init__(self, component_id: str,
                 start: tuple[int,int], end: tuple[int,int],
                 event_bus: EventBus):
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

        rect = QRectF(-40,-40,width,height)
        super().__init__(component_id, x, y, event_bus, rect, color="lightgreen")

    def paint(self, painter, option, widget=None):
        # Draw conveyor body
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor("darkgreen"), 2))
        painter.drawRect(self.rect)

        # Draw slots
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("black"), 1))

        slot_positions = []

        if self.is_vertical:
            for i in range(self.num_slots):
                top = -40 + i*100
                if i == 0:
                    rect = QRectF(-40, -40, 80, 80)
                elif i == self.num_slots-1:
                    rect = QRectF(-40, self.rect.height()-40-80, 80, 80)
                else:
                    rect = QRectF(-40, top, 80, 80)
                painter.drawRect(rect)
                slot_positions.append(rect.center())
        else:
            for i in range(self.num_slots):
                left = -40 + i*100
                if i == 0:
                    rect = QRectF(-40, -40, 80, 80)
                elif i == self.num_slots-1:
                    rect = QRectF(self.rect.width()-40-80, -40, 80, 80)
                else:
                    rect = QRectF(left, -40, 80, 80)
                painter.drawRect(rect)
                slot_positions.append(rect.center())

        # Draw direction arrows
        painter.setBrush(QBrush(QColor("darkgreen")))
        painter.setPen(Qt.PenStyle.NoPen)

        arrow_size = 20
        arrow_spacing = max(1, len(slot_positions) // 3)  # draw 3 arrows along conveyor
        for idx in range(0, len(slot_positions), arrow_spacing):
            pos = slot_positions[idx]
            arrow = QPolygonF()

            if self.is_vertical:
                # vertical conveyor: down or up
                if self.end[1] > self.start[1]:
                    # downward
                    arrow.append(QPointF(pos.x(), pos.y() + arrow_size/2))
                    arrow.append(QPointF(pos.x() - arrow_size/2, pos.y() - arrow_size/2))
                    arrow.append(QPointF(pos.x() + arrow_size/2, pos.y() - arrow_size/2))
                else:
                    # upward
                    arrow.append(QPointF(pos.x(), pos.y() - arrow_size/2))
                    arrow.append(QPointF(pos.x() - arrow_size/2, pos.y() + arrow_size/2))
                    arrow.append(QPointF(pos.x() + arrow_size/2, pos.y() + arrow_size/2))
            else:
                # horizontal conveyor: right or left
                if self.end[0] > self.start[0]:
                    # rightward
                    arrow.append(QPointF(pos.x() + arrow_size/2, pos.y()))
                    arrow.append(QPointF(pos.x() - arrow_size/2, pos.y() - arrow_size/2))
                    arrow.append(QPointF(pos.x() - arrow_size/2, pos.y() + arrow_size/2))
                else:
                    # leftward
                    arrow.append(QPointF(pos.x() - arrow_size/2, pos.y()))
                    arrow.append(QPointF(pos.x() + arrow_size/2, pos.y() - arrow_size/2))
                    arrow.append(QPointF(pos.x() + arrow_size/2, pos.y() + arrow_size/2))

            painter.drawPolygon(arrow)


class DepalletizerItem(BaseComponentItem):
    """
    A 100x100 rectangle that changes color when operating.
    Contains an internal 80x80 buffer
    """
    def __init__(self, component_id: str, coordinate: tuple[int, int], event_bus: EventBus):
        rect = QRectF(-50,-50,100,100)
        super().__init__(component_id, coordinate[0], coordinate[1], event_bus, rect, color="#AAAAAA")

        self.buffer_rect = QRectF(
            self.rect.x() + 10, # 10px margin all around
            self.rect.y() + 10,
            80,
            80
        )

        self.operating = False

        # Subscribe to events
        self.event_bus.subscribe("depalletizer_operating", self.on_operating)
        self.event_bus.subscribe("depalletizer_idle", self.on_idle)

    def on_operating(self, payload):
        """Called when the depalletizer starts working."""
        if payload.get("id") == self.id:
            self.operating = True
            self.color = QColor("#FFA500")  # orange = operating
            self.update()

    def on_idle(self, payload):
        """Called when the depalletizer stops."""
        if payload.get("id") == self.id:
            self.operating = False
            self.color = QColor("#808080")  # gray = idle
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


class BatchBuilderItem(BaseComponentItem):
    """
    A Batch Builder is similar to a PayloadBuffer but builds batches
    from depalletized items. It visually looks like an 80x80 block
    with two states: idle or building.
    """
    def __init__(self, component_id: str, coordinate: tuple[int, int], event_bus: EventBus):
        rect = QRectF(-40,-40,80,80)
        super().__init__(component_id, coordinate[0], coordinate[1], event_bus, rect, color="#808080") # default: idle gray

        self.operating = False

        # Make distinguishable from buffer
        self.border_color = QColor("black")
        self.border_thickness = 2

        # Subscribe to events
        self.event_bus.subscribe("batch_builder_building", self.on_building)
        self.event_bus.subscribe("batch_builder_idle", self.on_idle)

    def on_building(self, payload):
        """Switch to 'building' mode (active)."""
        if payload.get("id") == self.id:
            self.operating = True
            self.color = QColor("#FFA500")  # orange = building
            self.update()

    def on_idle(self, payload):
        """Switch back to 'idle' mode."""
        if payload.get("id") == self.id:
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


# ------------
# Stock items
# ------------

class BaseStockItem(BaseComponentItem):
    """
    Base model for a stock item
    """
    def __init__(self, stock_id: str, x: float, y: float, event_bus: EventBus, rect: QRectF, color, z=0):
        super().__init__(stock_id, x, y, event_bus, rect, color, z)

        # Track item and order count for visualization
        self.stock_count = 0
        self.fill_percentage = 0  # percentages (empty)
        self.order_count = 0

        # Text layout and font calculations
        padding = 10
        # Define dedicated areas for text inside the main rectangle
        content_rect = self.rect.adjusted(padding, padding, -padding, -padding)
        title_height = content_rect.height() * 0.3  # Reduced from 0.4 to leave more room
        info_height = (content_rect.height() - title_height) / 2

        self.title_rect = QRectF(content_rect.x(), content_rect.y(), content_rect.width(), title_height)
        self.stock_rect = QRectF(content_rect.x(), self.title_rect.bottom(), content_rect.width(), info_height)
        self.order_rect = QRectF(content_rect.x(), self.stock_rect.bottom(), content_rect.width(), info_height)

    def _get_optimal_font(self, text: str, rect: QRectF, bold: bool = False, font_family: str = "Segoe UI") -> QFont:
        """Calculates the largest QFont that fits the text within the given rectangle."""
        font = QFont(font_family)
        if bold:
            font.setWeight(QFont.Weight.Bold)

        # Binary search for best font size
        min_size, max_size = 4, 150
        optimal_size = min_size

        while min_size <= max_size:
            current_size = (min_size + max_size) // 2
            if current_size == 0:
                break

            font.setPixelSize(current_size)
            metrics = QFontMetrics(font)

            # Check if text fits both horizontally and vertically
            # Add some padding margin (90% of available space)
            text_rect = metrics.boundingRect(text)
            if text_rect.width() < rect.width() * 0.95 and text_rect.height() < rect.height() * 0.9:
                optimal_size = current_size
                min_size = current_size + 1  # It fits, so try a larger size
            else:
                max_size = current_size - 1  # It's too big, try a smaller size

        font.setPixelSize(optimal_size)
        return font

    def update_order_count(self, payload):
        """Updates the order count and schedules a repaint."""
        order_count = payload["count"]
        if type(order_count) == int:  # Validate payload
            self.order_count = order_count
            self.update()

    def update_stock_count(self, payload):
        """Updates the pallet count and schedules a repaint."""
        stock_count = payload["count"]
        fill_percentage = payload["fill"]
        if type(stock_count) == int and type(fill_percentage) == int:  # Validate payload
            self.stock_count = stock_count
            self.fill_percentage = fill_percentage
            self.update()

class WarehouseItem(BaseStockItem):
    """
    Visual representation of a warehouse between input and output buffers.
    Text is dynamically scaled to perfectly fit the item's dimensions.
    """
    def __init__(self, input_buffer_pos: tuple[int, int],
                 output_buffer_pos: tuple[int, int],
                 event_bus: EventBus):
        dx = output_buffer_pos[0] - input_buffer_pos[0]
        dy = output_buffer_pos[1] - input_buffer_pos[1]
        self.is_horizontal = abs(dx) > abs(dy)

        # Center position between buffers
        x = (input_buffer_pos[0] + output_buffer_pos[0]) / 2
        y = (input_buffer_pos[1] + output_buffer_pos[1]) / 2

        buffer_half = 40
        visual_gap = 10  # small space between buffers and warehouse

        if self.is_horizontal:
            # Width nearly reaches buffers but leaves small gap
            width = abs(dx) * 100 - 2 * (buffer_half + visual_gap)
            height = 160  # taller for visibility
        else:
            width = 160
            height = abs(dy) * 100 - 2 * (buffer_half + visual_gap)

        # Ensure minimum reasonable size
        width = max(width, 200)
        height = max(height, 160)

        rect = QRectF(-width / 2, -height / 2, width, height)
        super().__init__("warehouse", x, y, event_bus, rect, color="#d0e4f7")

        # Calculate the optimal font sizes once during initialization for performance
        # Use a placeholder for dynamic text to estimate the maximum required width
        self.title_font = self._get_optimal_font("Warehouse", self.title_rect, bold=True)
        self.info_font = self._get_optimal_font("Orders in queue: 99999", self.stock_rect)

        # Subscribe to events
        self.event_bus.subscribe("warehouse_pallet_count", self.update_stock_count)
        self.event_bus.subscribe("warehouse_order_count", self.update_order_count)

    def paint(self, painter, option, widget=None):
        """Draws the component background and its autofitting text."""
        # main body
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(QColor("#2a6ea9"), 2))
        painter.drawRect(self.rect)

        # title text
        painter.setPen(QColor("#0b3954"))
        painter.setFont(self.title_font)
        painter.drawText(self.title_rect, Qt.AlignmentFlag.AlignCenter, "Warehouse")

        # info text
        painter.setPen(QColor("#222222"))
        painter.setFont(self.info_font)
        painter.drawText(self.stock_rect, Qt.AlignmentFlag.AlignCenter, f"Pallets: {self.stock_count} ({self.fill_percentage}%)")
        painter.drawText(self.order_rect, Qt.AlignmentFlag.AlignCenter, f"Orders: {self.order_count}")


class ItemWarehouseItem(BaseStockItem):
    """
    Visual representation of an item warehouse.
    Buffers are either on top+bottom (horizontal) or left+right (vertical).
    Text is dynamically scaled to perfectly fit the item's dimensions.
    """

    def __init__(self, top_left_corner_pos: tuple[int, int],
                 bottom_right_corner_pos: tuple[int, int],
                 event_bus: EventBus,
                 buffers_horizontal: bool = True):
        BUFFER_HALF = 40
        VISUAL_GAP = 10

        min_x = top_left_corner_pos[0]
        max_x = bottom_right_corner_pos[0]
        min_y = top_left_corner_pos[1]
        max_y = bottom_right_corner_pos[1]

        if buffers_horizontal:
            # Buffers on top and bottom
            # Warehouse fits between them vertically, extends horizontally
            left = min_x * 100 - BUFFER_HALF - VISUAL_GAP
            right = max_x * 100 + BUFFER_HALF + VISUAL_GAP
            top = min_y * 100 + BUFFER_HALF + VISUAL_GAP
            bottom = max_y * 100 - BUFFER_HALF - VISUAL_GAP
        else:
            # Buffers on left and right
            # Warehouse fits between them horizontally, extends vertically
            left = min_x * 100 + BUFFER_HALF + VISUAL_GAP
            right = max_x * 100 - BUFFER_HALF - VISUAL_GAP
            top = min_y * 100 - BUFFER_HALF - VISUAL_GAP
            bottom = max_y * 100 + BUFFER_HALF + VISUAL_GAP

        # Calculate center position and dimensions
        x = (left + right) / 200
        y = (top + bottom) / 200
        width = abs(right - left)
        height = abs(bottom - top)

        # Ensure minimum reasonable size
        width = max(width, 200)
        height = max(height, 160)

        rect = QRectF(-width / 2, -height / 2, width, height)
        super().__init__("item_warehouse", x, y, event_bus, rect, color="#d0e4f7")

        # Calculate the optimal font sizes once during initialization for performance
        # Use a placeholder for dynamic text to estimate the maximum required width
        self.title_font = self._get_optimal_font("Item Warehouse", self.title_rect, bold=True)
        self.info_font = self._get_optimal_font("Orders in queue: 99999", self.stock_rect)

        # Subscribe to events
        self.event_bus.subscribe("item_warehouse_item_count", self.update_stock_count)
        self.event_bus.subscribe("item_warehouse_order_count", self.update_order_count)

    def paint(self, painter, option, widget=None):
        """Draws the component background and its autofitting text."""
        # main body
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(QColor("#2a6ea9"), 2))
        painter.drawRect(self.rect)

        # title text
        painter.setPen(QColor("#0b3954"))
        painter.setFont(self.title_font)
        painter.drawText(self.title_rect, Qt.AlignmentFlag.AlignCenter, "Item Warehouse")

        # info text
        painter.setPen(QColor("#222222"))
        painter.setFont(self.info_font)
        painter.drawText(self.stock_rect, Qt.AlignmentFlag.AlignCenter,
                         f"Items: {self.stock_count} ({self.fill_percentage}%)")
        painter.drawText(self.order_rect, Qt.AlignmentFlag.AlignCenter, f"Orders: {self.order_count}")

