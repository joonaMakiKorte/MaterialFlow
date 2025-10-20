from simulator.core.components.component import Component
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.gui.event_bus import EventBus
from simulator.core.transportation_units.transportation_unit import TransportationUnit
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.config import PALLET_BUFFER_PROCESS_TIME
import simpy


class Junction(Component):
    """
    Route payloads to different outputs.
    Routing is based on chosen handoff ratio per port.

    Additional Attributes
    ---------------------
    process_main : simpy.Process
        SimPy process instance for main routing loop.
    coordinate : tuple[int,int]
        Physical location of the junction.
    buffer : PayloadBuffer
        Buffer for payload handling.
    payload : SystemPallet
        Current pallet
    pallet_process_time : float
        Time to unload a pallet
    available_ports : dict[str, bool]
        Port availability keyed by port id
    ratio: list[int]
        The distribution ratio for pallets per port.
    """

    def __init__(self, env: simpy.Environment, junction_id: str, ratio: str,
                 coordinate: tuple[int, int], payload_process_time: float = PALLET_BUFFER_PROCESS_TIME):
        super().__init__(env, component_id=junction_id)
        self._coordinate = coordinate

        # Internal batch buffer
        self._buffer = PayloadBuffer(env=env,
                                     buffer_id=f"{junction_id}_buf",
                                     coordinate=coordinate,
                                     process_time=payload_process_time)
        self._payload: SystemPallet | None = None
        self._available_ports: dict[str, bool] = {}
        self._ratio = [int(r) for r in ratio.split(':')] # Get ratio

        # State for ratio-based routing
        self._port_order: list[str] = []
        self._current_port_index = 0
        self._pallets_sent_to_current_port = 0

        self.process_main = self.env.process(self._routing_loop())

    # -----------
    # Properties
    # -----------

    @property
    def coordinate(self) -> tuple[int,int]:
        return self._coordinate

    # --------
    #  Logic
    # --------

    def connect(self, component: "Component", port: str = "out"):
        """
        Override base connect.
        Delegate to internal buffer and update port tracking.
        """
        self._buffer.connect(component, port)
        self._available_ports[port] = True
        self._port_order = sorted(self._available_ports.keys())

    def inject_event_bus(self, event_bus: EventBus):
        """
        Override base event bus injection.
        Delegate to internal buffer.
        """
        self.event_bus = event_bus
        self._buffer.event_bus = event_bus

    def can_load(self) -> bool:
        return self._buffer.can_load()

    def load(self, payload: TransportationUnit):
        """Route payload through buffer first."""
        if self.can_load():
            self._buffer.load(payload)

    def _handoff_pallet(self, port: str):
        """Empty pallet leaves via buffer handoff."""
        yield from self._buffer.handoff(port)

    def _routing_loop(self):
        """Main routing loop."""
        while True:
            self._buffer.on_load_event = self.env.event()
            pallet = yield self._buffer.on_load_event  # wait for pallet

            if pallet is None:
                # Wait until a pallet exists
                yield self.env.timeout(0.5)
                continue

            # Ensure port order is updated if connections change dynamically
            if len(self._port_order) != len(self._available_ports):
                self._port_order = sorted(self._available_ports.keys())

            if not self._port_order:
                # No connected ports, wait
                yield self.env.timeout(1)
                continue

            # Find the next available port based on the ratio
            ports_checked = 0
            while ports_checked < len(self._port_order):
                port_id = self._port_order[self._current_port_index]

                if self._available_ports.get(port_id, False):
                    # Port is available, handoff the pallet
                    yield self.env.process(self._handoff_pallet(port_id))
                    self._pallets_sent_to_current_port += 1

                    # Check if we need to move to the next port in the ratio sequence
                    if self._pallets_sent_to_current_port >= self._ratio[self._current_port_index % len(self._ratio)]:
                        self._pallets_sent_to_current_port = 0
                        self._current_port_index = (self._current_port_index + 1) % len(self._port_order)

                    break  # Exit the loop after successful handoff
                else:
                    # Port is not available, move to the next port
                    self._current_port_index = (self._current_port_index + 1) % len(self._port_order)
                    self._pallets_sent_to_current_port = 0  # Reset count when skipping
                    ports_checked += 1
            else:
                # If we've looped through all ports and none are available, wait
                yield self.env.timeout(1)