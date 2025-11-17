import logging
from collections import deque
from typing import Deque
import simpy

def log_context(env: simpy.Environment):
    """Get sim time as log context."""
    return {'sim_time': round(env.now,1)}

class SimTimeFormatter(logging.Formatter):
    """
    A custom logging formatter that uses simulation time as the timestamp
    and the dynamic component_id as the logger name.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Overrides the default format method to dynamically insert component_id.
        """
        if hasattr(record, 'component_id'):
            original_name = record.name
            record.name = record.component_id

            # Let the parent class do the heavy lifting of formatting
            formatted_message = super().format(record)

            # Restore the original name in case the record is used elsewhere
            record.name = original_name

            return formatted_message

        # If no component_id is present, format as usual
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        if 'sim_time' in record.__dict__:
            # Round the simulation time for cleaner display
            return f"{round(record.sim_time, 2):8.2f}"
        else:
            return super().formatTime(record, datefmt)

class LogManager:
    """
    A stateful log system managing the application's logging,
    storing all logs and allowing for filtering.
    """
    def __init__(self, max_log_history: int = 100):
        self.all_logs: Deque[logging.LogRecord] = deque(maxlen=max_log_history)
        self.formatter = SimTimeFormatter("[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s")

        self.sim_logger = logging.getLogger("simulation_events")
        self.sim_logger.setLevel(logging.INFO)
        self.sim_logger.propagate = False

        if self.sim_logger.hasHandlers():
            self.sim_logger.handlers.clear()

        # A handler that will store all log records in our deque
        class StoreRecordsHandler(logging.Handler):
            def __init__(self, log_list: Deque):
                super().__init__()
                self.log_list = log_list

            def emit(self, record):
                self.log_list.append(record)

        store_handler = StoreRecordsHandler(self.all_logs)
        self.sim_logger.addHandler(store_handler)

    def log(self, message: str, component_id: str, sim_time: float, level=logging.INFO):
        """
        Logs a simulation-specific message, storing it for the UI.
        """
        extra = {
            'sim_time': sim_time,
            'component_id': component_id
        }

        self.sim_logger.log(level, message, extra=extra)

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