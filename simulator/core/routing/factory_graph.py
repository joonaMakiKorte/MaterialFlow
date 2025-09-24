from typing import Tuple, List
from simulator.config import CONVEYOR_CYCLE_TIME, BUFFER_PROCESS_TIME
from simulator.core.factory.factory import Factory
from simulator.core.components.component import Component


class Edge:
    def __init__(self, target: Tuple[int,str], base_weight: float = 1.0):
        """
        Definition for the graph-edge.

        Attributes
        ----------
        target : Tuple[int,str]
            Id and type of target component.
        base_weight : float
            Static component of edge weight based on geometry and base process times.
        """
        self.target = target
        self.base_weight = base_weight

class FactoryGraph:
    """
    Represents the factory layout and handles routing between components.
    Represents components as nodes and connections as edges.

    Attributes
    ----------
    factory : Factory
        Instance of factory for accessing Component info
    adjacency : dict[int,List[Edge]]
        Adjacency list: component -> edges
    router : Router
        Access routing functions

    """
    def __init__(self, factory: Factory):
        self._factory = factory
        self._adjacency: dict[int,List[Edge]] = {}

    # -----------
    # Properties
    # -----------

    # ---------------
    # Private helpers
    # ---------------


    # --------------
    # Public methods
    # --------------

    def add_node(self, component_id: int):
        # Ensure component is not in adjacency
        if component_id not in self._adjacency:
            self._adjacency[component_id] = [] # Empty list for storing edges

    def add_edge(self, source_id: int, target_id: int, target_type: str, base_weight: float):
        """Add directed edge between components."""
        # For safety try creating new nodes
        self.add_node(source_id)
        self.add_node(target_id)

        self._adjacency[source_id].append(Edge(target=(target_id, target_type),base_weight=base_weight))

