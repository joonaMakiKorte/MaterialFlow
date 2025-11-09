from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import QSize
from simulator.gui.factory_scene import FactoryScene

class FactoryView(QGraphicsView):
    """
    A custom QGraphicsView that automatically tells its scene to rescale
    whenever the view itself is resized.
    """

    def __init__(self, scene: "FactoryScene", parent=None):
        super().__init__(scene, parent)

    def resizeEvent(self, event):
        """
        This method is automatically called by PyQt whenever the widget is resized.
        """
        # Call the parent class's resizeEvent to handle default behavior
        super().resizeEvent(event)

        # Get the new size of this view widget
        new_size: QSize = event.size()

        # Tell the scene to rescale its contents to fit our new size
        if self.scene():
            self.scene().scale_scene(new_size.width(), new_size.height())