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
        """
        Overrides the default time formatting.
        If 'sim_time' is in the record, it's used.
        Otherwise, it falls back to the default real-time formatter.
        """
        if hasattr(record, 'sim_time'):
            # Format the simulation time as a floating point number
            return f"{record.sim_time:8.2f}"
        else:
            # Fallback for non-simulation logs
            return super().formatTime(record, datefmt)

class LogManager:
    """Manages the application's logging configuration."""
    def __init__(self, max_log_history: int = 100):
        self.recent_logs: Deque[str] = deque(maxlen=max_log_history)
        self._setup_logging()

    def _setup_logging(self):
        """Configures the root logger with our custom handlers."""
        # The format string uses %(asctime)s, but our custom
        # formatter will populate it with the simulation time.
        log_format = "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s"
        formatter = SimTimeFormatter(log_format)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        list_handler = ListHandler(self.recent_logs)
        list_handler.setFormatter(formatter)
        root_logger.addHandler(list_handler)

    def get_recent_logs(self) -> list[str]:
        """Returns the list of recent log messages."""
        return list(self.recent_logs)


def get_logger(name, log_list: Deque[str]) -> logging.Logger:
    """Returns a logger instance for a specific module."""
    logger = logging.getLogger(str(name))
    logger.setLevel(logging.INFO)  # Set the threshold
    local_handler = ListHandler(log_list)  # Handler that writes to this instance's specific log list

    # A simpler format for the component's internal log view.
    formatter = SimTimeFormatter("[%(asctime)s] %(message)s")
    local_handler.setFormatter(formatter)

    # Add the local handler to the component's logger
    logger.addHandler(local_handler)

    # Ensure logs also go to the root logger for the global view
    logger.propagate = True

    return logger