import simpy
from simulator.core.components.component import Component
from simulator.core.transportation_units.system_pallet import SystemPallet
from typing import Tuple, Optional
from simulator.config import BUFFER_PROCESS_TIME

class PayloadBuffer(Component):
    """
    Buffer component between logical and physical flows.
    Main role is to move and store payloads between components (e.g. Input-Output-station)

    Additional Attributes
    ----------
    coordinate : Tuple[float,float]
        Physical location of the buffer.
    process_time : float
        Time in simulation units per movement cycle (processing delay).
    payload : SystemPallet
        SystemPallet occupying the buffer.
    on_load_event : simpy.events.Event
        Event triggered by loading a pallet on the buffer.
    """
    def __init__(self, buffer_id: int,
                 coordinate: Tuple[float,float], process_time: float = BUFFER_PROCESS_TIME):
        super().__init__(buffer_id)
        self._coordinate = coordinate
        self._process_time = process_time
        self._payload: Optional[SystemPallet] = None
        self.on_load_event = None

        # Calculate process time
        self._static_process_time = self._get_static_process_time()

    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> Tuple[float,float]:
        return self._coordinate

    @property
    def payload(self) -> Optional[SystemPallet]:
        return self._payload

    # ---------------
    # Private helpers
    # ---------------

    def _get_static_process_time(self) -> float:
        return self._process_time

    # ---------
    #   Logic
    # ---------

    def inject_env(self, env: simpy.Environment):
        self.env = env

    def can_load(self) -> bool:
        """No payload -> can load."""
        return self.payload is None

    def load(self, pallet: SystemPallet):
        """Update pallet on buffer."""
        if self.can_load():
            self._payload = pallet
            pallet.actual_location.update(coordinates=self.coordinate, element_name=f"{self}")
            print(f"[{self.env.now}] {self}: Loaded {pallet}")

            # Fire event if buffer owner is waiting
            if self.on_load_event and not self.on_load_event.triggered:
                self.on_load_event.succeed(pallet)
                self.on_load_event = None

    def handoff(self):
        """Unload pallet to downstream."""
        if self._output and self._payload is not None:
            yield self.env.timeout(self._process_time)  # process delay
            print(f"[{self.env.now}] {self}: Unloaded {self._payload}")
            self._output.load(self._payload)
            self._payload = None
