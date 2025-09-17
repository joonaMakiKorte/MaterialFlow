import simpy
from simulator.core.components.component import Component
from simulator.core.transportation_units.system_pallet import SystemPallet
from typing import Tuple, Optional


class PayloadBuffer(Component):
    """
    Buffer component between logical and physical flows.
    Main role is to move and store payloads between components (e.g. Input-Output-station)

    Additional Attributes
    ----------
    coordinate : Tuple[float,float]
        Location of the buffer.
    cycle_time : float
        Time in simulation units per movement cycle (processing delay).
    payload : SystemPallet
        SystemPallet occupying the buffer.
    on_load_event : simpy.events.Event
        Event triggered by loading a pallet on the buffer.
    """

    def __init__(self, env: simpy.Environment, buffer_id: int,
                 coordinate: Tuple[float,float], cycle_time: float):
        super().__init__(env, buffer_id)
        self._coordinate = coordinate
        self._cycle_time = cycle_time
        self._payload: Optional[SystemPallet] = None
        self.on_load_event = None

    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> Tuple[float,float]:
        return self._coordinate

    @property
    def cycle_time(self) -> float:
        return self._cycle_time

    @property
    def payload(self) -> Optional[SystemPallet]:
        return self._payload

    @payload.setter
    def payload(self, new_payload):
        """Set a new payload with type checking."""
        if new_payload is not None and not isinstance(new_payload, SystemPallet):
            raise ValueError("payload must be a SystemPallet")
        self._payload = new_payload

    # ---------
    #   Logic
    # ---------

    def can_load(self) -> bool:
        """No payload -> can load."""
        return self.payload is None

    def load(self, pallet: SystemPallet):
        """Update pallet on buffer."""
        if self.can_load():
            self.payload = pallet
            pallet.actual_location.update(coordinates=self.coordinate, element_name=f"{self}")
            print(f"[{self.env.now}] {self}: Loaded {pallet}")

            # Fire event if buffer owner is waiting
            if self.on_load_event and not self.on_load_event.triggered:
                self.on_load_event.succeed(pallet)
                self.on_load_event = None

    def handoff(self, downstream_idx: int):
        """Unload pallet to selected downstream."""
        if self.payload is None:
            print(f"[{self.env.now}] {self}: No payload to hand off")
            return
        if downstream_idx >= len(self.downstream):
            raise IndexError(f"{self}: Invalid downstream index {downstream_idx}")

        if len(self.downstream) != 0:
            pallet = self.payload
            self.payload = None
            yield self.env.timeout(self.cycle_time)  # process delay
            self.downstream[downstream_idx].load(pallet)
            print(f"[{self.env.now}] {self}: Handed off {pallet} to {self.downstream[downstream_idx]}")
