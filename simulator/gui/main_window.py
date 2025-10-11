from PyQt6.QtWidgets import QMainWindow, QGraphicsView
from simulator.gui.factory_scene import FactoryScene

class MainWindow(QMainWindow):
    def __init__(self, scene: FactoryScene):
        super().__init__()
        self.setWindowTitle("Material Flow")

        # Graphics view for system flow
        self.view = QGraphicsView()
        self.scene = scene
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
