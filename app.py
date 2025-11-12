import sys
import logging
from simulator.application import Application
from PyQt6.QtWidgets import QApplication

def main():
    # Setup logging to the terminal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.info("Application starting up...")

    app = QApplication(sys.argv)
    application = Application()
    application.run()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()