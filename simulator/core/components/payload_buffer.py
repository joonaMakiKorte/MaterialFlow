import simpy
from simulator.core.components.component import Component
from simulator.core.transportation_units.system_pallet import TransportationUnit
from simulator.config import PALLET_BUFFER_PROCESS_TIME
from simulator.core.utils.logging_config import log_manager


class PayloadBuffer(Component):
    """
    Buffer component between logical and physical flows.
    Main role is to move and store payloads between components (e.g. Input-Output-station)

    Additional Attributes
    ----------
    coordinate : Tuple[int,int]
        Physical location of the buffer.
    process_time : float
        Time in simulation units per movement cycle (processing delay).
    payload : TrasportationUnit
        Payload occupying the buffer.
    on_load_event : simpy.events.Event
        Event triggered by loading a payload on the buffer.
    """
    def __init__(self, env: simpy.Environment, buffer_id: str,
                 coordinate: tuple[int,int], process_time: float = PALLET_BUFFER_PROCESS_TIME):
        super().__init__(env, component_id=buffer_id)
        self._coordinate = coordinate
        self._process_time = process_time
        self._payload: TransportationUnit | None = None
        self.on_load_event = None


    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> tuple[int,int]:
        return self._coordinate

    @property
    def payload(self) -> TransportationUnit | None:
        return self._payload

    # ---------
    #   Logic
    # ---------

    def can_load(self) -> bool:
        """No payload -> can load."""
        return self.payload is None

    def load(self, payload: TransportationUnit):
        """Update payload on buffer."""
        if self.can_load():
            self._payload = payload
            payload.actual_location.update(coordinates=self._coordinate, element_name=f"{self}")

            log_manager.log(f"Loaded {payload}", f"{self}", sim_time=self.env.now)

            # Notify gui of event
            if self.event_bus is not None:
                self.event_bus.emit("move_payload", {"id":payload.id, "coords":self._coordinate})

            # Fire event if buffer owner is waiting
            if self.on_load_event and not self.on_load_event.triggered:
                self.on_load_event.succeed(payload)
                self.on_load_event = None

    def handoff(self, port: str = "out"):
        """Unload payload to downstream."""
        # Choose output element
        if port == "out":
            output = self._output
        else:
            output = self._outputs.get(port)

        if output and self._payload is not None:
            # Wait until output becomes available for loading
            while not output.can_load():
                yield self.env.timeout(0.5)

            yield self.env.timeout(self._process_time)  # process delay
            log_manager.log(f"Unloaded {self._payload} to {output}", f"{self}", sim_time=self.env.now)
            output.load(self._payload)
            self._payload = None

    def clear(self):
        """Clear any payload from buffer"""
        self._payload = None