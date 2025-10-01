import simpy
from simulator.core.components.component import Component
from simulator.core.transportation_units.transportation_unit import TransportationUnit
from typing import List, Tuple, Optional
from simulator.config import CONVEYOR_CYCLE_TIME

class PayloadConveyor(Component):
    """
    Used for transporting TransportationUnits from point to another.
    Capacity is determined by number of discrete 'action points' (slots).
    Has a fixed operation direction.
    Conceptually acts like a small queue with positions.

    Additional Attributes
    ----------
    process : simpy.Process
        SimPy process instance for this component.
    start : Tuple[float,float]
        Entry point of the conveyor for payloads.
    end : Tuple[float,float]
        payload output from conveyor.
    num_slots : int
        The amount of payloads the conveyor can fit.
    cycle_time : float
        Time in simulation units per movement cycle.
    slots : List[Optional[TransportationUnit]]
        List of either 'None' or payload IDs. Conveyor length == num of slots.
    slot_coords : List[Tuple[float,float]]
        List of each slot coordinate.
    """
    def __init__(self, env: simpy.Environment, conveyor_id: str,
                 start: Tuple[float, float], end: Tuple[float, float],
                 num_slots: int, cycle_time: float = CONVEYOR_CYCLE_TIME):
        super().__init__(env,component_id=conveyor_id, static_process_time=num_slots * cycle_time)
        self.process = env.process(self._run())
        self._start = start
        self._end = end
        self._num_slots = num_slots
        self._cycle_time = cycle_time

        # Internal slots
        self._slots: List[Optional[TransportationUnit]] = [None] * num_slots
        self._slot_coords = self._calculate_slots(start, end, num_slots)

    # ----------
    # Properties
    # ----------

    @property
    def start(self) -> Tuple[float, float]:
        return self._start

    @property
    def end(self) -> Tuple[float, float]:
        return self._end

    @property
    def num_slots(self) -> int:
        return self._num_slots

    @property
    def slots(self) -> List[Optional[TransportationUnit]]:
        """Read-only view of slot contents"""
        return self._slots


    # ---------------
    # Private Helpers
    # ---------------

    def _calculate_slots(self, start: Tuple[float, float],
                         end: Tuple[float, float],
                         num_slots: int) -> List[Tuple[float, float]]:
        """Return evenly spaced slot coordinates"""
        if num_slots == 2:
            return [start, end]

        x1, y1 = map(float, start)
        x2, y2 = map(float, end)

        slots = []
        for i in range(num_slots):
            t = i / (num_slots - 1)  # normalized 0..1
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            slots.append((x, y))

        return slots

    # -------
    #  Logic
    # -------

    def can_load(self) -> bool:
        """Check if first slot is free for loading"""
        return self.slots[0] is None

    def load(self, payload: TransportationUnit):
        """Place payload at start if free"""
        if self.can_load():
            self.slots[0] = payload
            payload.actual_location.update(coordinates=self._slot_coords[0], element_name=f"{self}")
            print(f"[{self.env.now}] {self}: Loaded {payload}")

    def shift(self):
        """Shift transportation units one slot forward if possible."""
        # Try to unload the last slot into downstream
        if self._output and self.slots[-1] is not None:
            payload = self.slots[-1]
            if self._output.can_load():
                self.env.process(self._handoff(payload, self._output))
                self.slots[-1] = None

        # Traverse backwards to not overwrite slots
        for i in reversed(range(1, self.num_slots)):
            if self.slots[i] is None and self.slots[i - 1] is not None:
                payload = self.slots[i - 1]
                payload.actual_location.update(coordinates=self._slot_coords[i])
                self.slots[i] = self.slots[i - 1]
                self.slots[i - 1] = None

    def _handoff(self, payload: TransportationUnit, downstream):
        """Schedule payload unloading for the downstream elements next event turn"""
        yield self.env.timeout(0)  # schedule for "next event turn"
        print(f"[{self.env.now}] {self}: Unloaded {payload}")
        downstream.load(payload)

    def _run(self):
        """Main conveyor loop."""
        while True:
            yield self.env.timeout(self._cycle_time)
            self.shift()