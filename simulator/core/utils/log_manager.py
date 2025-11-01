import logging
from collections import deque
from typing import Deque
import simpy

class ListHandler(logging.Handler):
    """A logging handler that keeps a list of recent logs."""
    def __init__(self, log_list: Deque):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        self.log_list.append(self.format(record))

def log_context(env: simpy.Environment):
    """Get sim time as log context."""
    return {'sim_time': round(env.now,1)}

class SimTimeFormatter(logging.Formatter):
    """
    A custom logging formatter for using simulation time as timestamps in logs.
    """
    def formatTime(self, record, datefmt=None):
        if 'sim_time' in record.__dict__:
            # Round the simulation time for cleaner display
            return f"{round(record.sim_time, 2):8.2f}"
        else:
            return super().formatTime(record, datefmt)

class LogManager:
    """Manages the application's logging, storing all logs and allowing for filtering."""
    def __init__(self, max_log_history: int = 100):
        self.all_logs: Deque[logging.LogRecord] = deque(maxlen=max_log_history)
        self.formatter = SimTimeFormatter("[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s")
        self._setup_logging()

    def _setup_logging(self):
        """Configures the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # A handler that will store all log records in our deque
        class StoreRecordsHandler(logging.Handler):
            def __init__(self, log_list: Deque):
                super().__init__()
                self.log_list = log_list

            def emit(self, record):
                self.log_list.append(record)

        store_handler = StoreRecordsHandler(self.all_logs)
        root_logger.addHandler(store_handler)

    def log(self, message: str, component_id: str, sim_time: float, level=logging.INFO):
        """
        Logs a message from a component.
        """
        extra = {
            'sim_time': sim_time,
            'component_id': component_id
        }

        logger = logging.getLogger(component_id)
        logger.log(level, message, extra=extra)

    def get_unique_component_ids(self) -> list[str]:
        """
        Scans all stored log records and returns a sorted list of unique
        component IDs.
        """
        # A set is used to automatically handle uniqueness.
        all_ids = {
            getattr(record, 'component_id', None) for record in self.all_logs
        }
        # Remove None if it exists and return a sorted list for a stable order.
        all_ids.discard(None)
        return sorted(list(all_ids))

    def get_all_logs(self) -> list[str]:
        """Returns a formatted list of all log messages."""
        return [self.formatter.format(record) for record in self.all_logs]

    def get_component_logs(self, component_id: str) -> list[str]:
        """Returns a formatted list of log messages for a specific component."""
        return [self.formatter.format(record) for record in self.all_logs if getattr(record, 'component_id', None) == component_id]