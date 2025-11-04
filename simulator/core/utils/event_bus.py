from collections import defaultdict

class EventBus:
    """
    Stateless service for signaling system state changes to other components.
    """
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback):
        self._subscribers[event_type].append(callback)

    def emit(self, event_type: str, data=None):
        for callback in self._subscribers[event_type]:
            callback(data)