from simulator.application import Application
from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)

    application = Application()
    application.run()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()