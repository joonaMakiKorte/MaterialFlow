import simpy
from simulator.core.components.component import Component
from simulator.core.transportation_units.transportation_unit import TransportationUnit
from typing import List
from simulator.config import CONVEYOR_CYCLE_TIME
from simulator.core.utils.logging_config import log_manager


class PayloadConveyor(Component):
    """
    Used for transporting TransportationUnits from point to another.
    Capacity is determined by number of discrete 'action points' (slots).
    Has a fixed operation direction.
    Conceptually acts like a small queue with positions.

    Additional Attributes
    ----------
    process_conveying : simpy.Process
        SimPy process instance of main conveying loop.
    start : Tuple[int,int]
        Entry point of the conveyor for payloads.
    end : Tuple[int,int]
        payload output from conveyor.
    num_slots : int
        The amount of payloads the conveyor can fit.
    cycle_time : float
        Time in simulation units per movement cycle.
    slots : List[TransportationUnit]
        List of either 'None' or payload IDs. Conveyor length == num of slots.
    slot_coords : List[Tuple[int,int]]
        List of each slot coordinate.
    previously_loaded : bool
        Flag to track if conveyor was previously loaded
    """
    def __init__(self, env: simpy.Environment, conveyor_id: str,
                 start: tuple[int,int], end: tuple[int,int],
                 cycle_time: float = CONVEYOR_CYCLE_TIME):
        # Make sure conveyor is on x- or y-axis and not of length 1
        if not (start[0] == end[0] or start[1] == end[1]) and start != end:
            raise ValueError(f"Conveyor {conveyor_id} must be set along x- or y-axis and longer than 1 slot.")
        self._start = start
        self._end = end

        # Calculate number of slots (determined by length)
        self._num_slots = max(abs(start[0]-end[0]),abs(start[1]-end[1])) + 1

        super().__init__(env,component_id=conveyor_id)
        self.process_conveying = env.process(self._conveying_loop())
        self._cycle_time = cycle_time

        # Internal slots
        self._slots: list[TransportationUnit | None] = [None] * self._num_slots
        self._slot_coords = self._calculate_slots(start, end, self._num_slots)

        self.previously_loaded = False

    # ----------
    # Properties
    # ----------

    @property
    def start(self) -> tuple[int,int]:
        return self._start

    @property
    def end(self) -> tuple[int,int]:
        return self._end

    @property
    def num_slots(self) -> int:
        return self._num_slots

    @property
    def slots(self) -> list[TransportationUnit | None]:
        """Read-only view of slot contents"""
        return self._slots

    # ---------------
    # Private Helpers
    # ---------------

    def _calculate_slots(self, start: tuple[int,int],
                         end: tuple[int,int],
                         num_slots: int) -> List[tuple[int,int]]:
        """Return evenly spaced slot coordinates"""
        if num_slots == 2:
            return [start, end]

        x1, y1 = map(int, start)
        x2, y2 = map(int, end)

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
        return self._slots[0] is None

    def load(self, payload: TransportationUnit):
        """Place payload at start if free"""
        if self.can_load():
            self._slots[0] = payload
            payload.location.update(coordinates=self._slot_coords[0], element_name=f"{self}")

            log_manager.log(f"Loaded {payload}", f"{self}", sim_time=self.env.now)

            # Notify gui of event
            if self.event_bus is not None:
                self.event_bus.emit("move_payload", {
                    "id":payload.id,
                    "sim_time": self.env.now,
                    "type": payload.__class__.__name__,
                    "location": f"{payload.location}",
                    "coords":self._slot_coords[0]})

            self.previously_loaded = True

    def shift(self):
        """Shift transportation units one slot forward if possible."""
        # Try to unload the last slot into downstream
        if self._output and self._slots[-1] is not None:
            payload = self._slots[-1]
            if self._output.can_load():
                self.env.process(self._handoff(payload, self._output))
                self._slots[-1] = None

        # Traverse backwards to not overwrite slots
        for i in reversed(range(1, self.num_slots)):
            if self._slots[i] is None and self._slots[i - 1] is not None:
                if i == 0 and self.previously_loaded:
                    # Skip shifting if pallet was just loaded
                    break

                payload = self._slots[i - 1]
                payload.location.update(coordinates=self._slot_coords[i])
                self._slots[i] = self._slots[i - 1]
                self._slots[i - 1] = None

                # Notify gui of event
                if self.event_bus is not None:
                    self.event_bus.emit("move_payload", {
                        "id": payload.id,
                        "sim_time": self.env.now,
                        "type": payload.__class__.__name__,
                        "location": f"{payload.location}",
                        "coords": self._slot_coords[i]})

        self.previously_loaded = False

    def _handoff(self, payload: TransportationUnit, downstream):
        """Schedule payload unloading for the downstream elements next event turn"""
        yield self.env.timeout(0)  # schedule for "next event turn"
        log_manager.log(f"Unloaded {payload} to {downstream}", f"{self}", sim_time=self.env.now)
        downstream.load(payload)

    def _conveying_loop(self):
        """Main conveyor loop."""
        while True:
            while all(slot is None for slot in self._slots):
                # Wait until conveyor is non-empty
                yield self.env.timeout(0.5)

            yield self.env.timeout(self._cycle_time)
            self.shift()