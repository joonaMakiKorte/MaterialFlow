from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsScene
from simulator.gui.component_items import BaseItem, PalletItem
from simulator.gui.loader import load_component_items
from simulator.core.factory.factory import Factory
from simulator.gui.event_bus import EventBus

class FactoryScene(QGraphicsScene):
    """

    Attributes
    ----------
    gui_items : dict[str,'BaseComponentItem']
        GUI components of the factory keyed by id.
    event_bus : EventBus
        Bridge for the communication between simulator engine and gui.
    """
    def __init__(self, factory: Factory):
        super().__init__()
        self.gui_items: dict[str, "BaseItem"] = {}
        self.event_bus = EventBus()

        # Create component items based on factory
        load_component_items(self.gui_items, factory.components, factory.pallets)

        # Pass event bus for simulator
        factory.inject_eventbus(self.event_bus)

        # Initial rendering of each visible component
        for component_item in self.gui_items.values():
            self.addItem(component_item)

    def toggle_payload_visibility(self, payload_id: int, visible: bool):
        payload_item = self.gui_items.get(str(payload_id))
        if not payload_item:
            print(f"No item for payload with id({payload_id}).")
            return

        if isinstance(payload_item, PalletItem):
            if visible:
                payload_item.show_pallet()
            else:
                payload_item.hide_pallet()

    def update_payload_position(self, payload_id: int, new_pos: tuple[int,int]):
        payload_item = self.gui_items.get(str(payload_id))
        if not payload_item:
            print(f"No item for payload with id({payload_id}).")
            return

        if isinstance(payload_item, PalletItem):
            payload_item.update_position(new_pos)

    def update_pallet_state(self, pallet_id: int, new_state):
        pallet_item = self.gui_items.get(str(pallet_id))
        if not pallet_item:
            print(f"No item for pallet with id({pallet_id}).")
            return

        if isinstance(pallet_item, PalletItem):
            pallet_item.set_state(new_state)