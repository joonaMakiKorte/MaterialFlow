from PyQt6.QtWidgets import QGraphicsScene
from simulator.gui.component_items import BasePayloadItem, PalletItem, BatchItem
from simulator.gui.loader import load_items
from simulator.core.factory.factory import Factory

PAYLOAD_ITEM_TYPES = {
        "SystemPallet" : PalletItem,
        "ItemBatch" : BatchItem
    }

class FactoryScene(QGraphicsScene):
    """
    Main scene for visualizing factory simulation.
    Implements event handlers to update gui based on simulation events.
    """
    def __init__(self, factory: Factory):
        super().__init__()
        # Graphical items
        self.component_items: dict[str, "BaseComponentItem"] = {}
        self.payload_items: dict[int, "BasePayloadItem"] = {}

        # Store instance for event bus
        self.event_bus = factory.event_bus

        # Load items based on factory layout
        load_items(component_items=self.component_items,
                   factory=factory)

        self.scale = 0.0  # Calculated when scaling scene to screen



    def _compute_factory_dimensions(self):
        """Get bounding dimensions of factory."""
        xs = [c.x for c in self.component_items.values()]
        ys = [c.y for c in self.component_items.values()]

        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.factory_w = self.max_x - self.min_x
        self.factory_h = self.max_y - self.min_y

    def _compute_initial_scene_scale(self, screen_w, screen_h):
        """Compute initial scale based on screen dimensions."""
        # Base pixel scale
        base_scale = 100.0

        # Convert factory dimensions to pixel size at base scale
        factory_px_w = self.factory_w * base_scale
        factory_px_h = self.factory_h * base_scale

        # Margin so items aren’t flush with window edges
        margin = 0.1
        available_w = screen_w * (1 - 2 * margin)
        available_h = screen_h * (1 - 2 * margin)

        # Fit the factory inside the screen, preserving aspect ratio
        fit_scale = min(available_w / factory_px_w, available_h / factory_px_h)
        return base_scale * fit_scale

    def _map_to_scene(self, x: float, y: float):
        """Map simulation coordinates to scene coordinates (px)."""
        sim_x = x - self.min_x
        sim_y = y - self.min_y

        # Convert to pixel position
        pixel_x = sim_x * self.scale
        pixel_y = sim_y * self.scale

        return pixel_x, pixel_y

    def _add_components(self):
        """Initial rendering of each visible component."""
        for gui_item in self.component_items.values():
            pixel_x, pixel_y = self._map_to_scene(gui_item.x, gui_item.y)

            gui_item.setPos(pixel_x, pixel_y)
            gui_item.setScale(self.scale / 100) # Normalize size to match intended scale
            self.addItem(gui_item)

    def scale_scene(self, view_w: int, view_h: int):
        """Scale each component to scene."""
        # Compute factory dimensions from component data
        self._compute_factory_dimensions()

        # Compute and apply scale
        scale = self._compute_initial_scene_scale(view_w, view_h)
        self.scale = scale

        # Position and scale all items
        self._add_components()

    # --------------
    # Scene updating
    # --------------

    def create_payload(self, payload_id: int, payload_type: str):
        """Toggle visibility of payload."""
        if payload_type not in PAYLOAD_ITEM_TYPES:
            print(f"Unknown payload type: {payload_type}")
            return

        # Create gui item for payload and add to scene
        cls = PAYLOAD_ITEM_TYPES[payload_type]
        payload_item = cls()
        payload_item.setScale(self.scale / 100) # Adjust scale
        self.payload_items[payload_id] = payload_item
        self.addItem(payload_item)

    def delete_payload(self, payload_id: int):
        payload_item = self.payload_items.get(payload_id)
        if not payload_item:
            print(f"No item for payload with id({payload_id}).")
            return
        self.removeItem(payload_item)
        self.payload_items.pop(payload_id)

    def update_payload_position(self, payload_id: int, new_pos: tuple[int,int]):
        """Update position of payload. Gets mapped to correct scene coordinates."""
        payload_item = self.payload_items.get(payload_id)
        if not payload_item:
            print(f"No item for payload with id({payload_id}).")
            return

        if isinstance(payload_item, BasePayloadItem):
            # Convert coordinates to pixel coordinates
            pixel_x, pixel_y = self._map_to_scene(new_pos[0], new_pos[1])
            payload_item.update_position(pixel_x, pixel_y)

    def update_payload_state(self, payload_id: int, new_state):
        """Update """
        payload_item = self.payload_items.get(payload_id)
        if not payload_item:
            print(f"No item for payload with id({payload_id}).")
            return

        payload_item.set_state(new_state)

