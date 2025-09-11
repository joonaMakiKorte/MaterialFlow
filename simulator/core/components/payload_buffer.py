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
    """

    def __init__(self, env: simpy.Environment, buffer_id: int, name: str,
                 coordinate: Tuple[float,float], cycle_time: float):
        super().__init__(env, buffer_id, name)
        self.coordinate = coordinate
        self.cycle_time = cycle_time
        self.payload: Optional[SystemPallet] = None

    def can_load(self) -> bool:
        """No payload -> can load."""
        return self.payload is None

    def load(self, pallet: SystemPallet):
        """Update pallet on buffer."""
        if not self.can_load():
            print(f"[{self.env.now}] {self.name}: Buffer occupied!")
            return False
        self.payload = pallet
        pallet.actual_dest = self.coordinate
        print(f"[{self.env.now}] {self.name}: Loaded {pallet}")
        return True

    def handoff(self, downstream_idx: int):
        """Unload pallet to selected downstream."""
        if self.payload is None:
            print(f"[{self.env.now}] {self.name}: No payload to hand off")
            return
        if downstream_idx >= len(self.downstream):
            raise IndexError(f"{self.name}: Invalid downstream index {downstream_idx}")

        pallet = self.payload
        self.payload = None
        yield self.env.timeout(self.cycle_time)  # process delay
        self.downstream[downstream_idx].load(pallet)
        print(f"[{self.env.now}] {self.name}: Handed off {pallet} to {self.downstream[downstream_idx].name}")
