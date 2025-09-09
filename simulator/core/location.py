class Location:
    """
    Represents a point in space tied to a system component
    """
    def __init__(self, name: str, x: int, y: int, component: object = None):
        self.name = name
        self.x = x
        self.y = y
        self.component = component  # e.g., Conveyor, Depalletizer, Warehouse

    def __repr__(self):
        return f"<Location {self.name} ({self.x}, {self.y})>"