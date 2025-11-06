import simpy
from simulator.core.components.component import Component
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.transportation_units.transportation_unit import Location
from simulator.core.transportation_units.item_batch import ItemBatch
from simulator.config import BATCH_BUFFER_PROCESS_TIME, BATCH_MAX_WAIT_TIME
from simulator.core.utils.id_gen_config import id_generator
from simulator.gui.component_items import BatchState
from simulator.core.utils.event_bus import EventBus
from simulator.core.utils.logging_config import log_manager


class BatchBuilder(Component):
    """
    Builds ItemBatches from individual items.
    Batches are build on a payload buffer and handed downstream when ready.
    A new Batch is created when the item is loaded on an empty buffer.

    Additional Attributes
    ---------------------
    process_main : simpy.Process
        SimPy process instance for main batch building loop.
    coordinate : Tuple[int,int]
        Physical location of the batch builder.
    buffer : PayloadBuffer
        Buffer for Batch building.
    current_batch : ItemBatch
        Current batch being built
    """
    def __init__(self, env: simpy.Environment, builder_id: str,
                 coordinate : tuple[int,int],
                 batch_process_time: float = BATCH_BUFFER_PROCESS_TIME):
        super().__init__(env, component_id=builder_id)
        self.process_main = env.process(self._build_loop()) # Register run loop
        self._coordinate = coordinate
        self._batch_process_time = batch_process_time

        # Internal batch buffer
        self._buffer = PayloadBuffer(env=env,
                                     buffer_id=f"{builder_id}_buf",
                                     coordinate=coordinate,
                                     process_time=batch_process_time)

        self._current_batch : ItemBatch | None = None

    # ----------
    # Properties
    # ----------

    @property
    def coordinate(self) -> tuple[int,int]:
        return self._coordinate

    @property
    def buffer(self) -> PayloadBuffer:
        return self._buffer

    @property
    def payload(self) -> ItemBatch | None:
        return self._buffer.payload

    # --------
    #  Logic
    # --------

    def connect(self, component: "Component", port: str = "out"):
        """
        Override base connect.
        Delegate to internal buffer.
        """
        self._buffer.connect(component, port="out")

    def inject_event_bus(self, event_bus: EventBus):
        """
        Override base event bus injection.
        Delegate to internal buffer.
        """
        self.event_bus = event_bus
        self._buffer.event_bus = event_bus

    def can_load(self) -> bool:
        """Technically can be loaded any time since has batches built upon."""
        return True

    def load(self, item_id : int) -> bool:
        """
        If buffer is empty, creates a new ItemBatch to build on,
        otherwise places items on the existing batch.
        Return truth value indicating load success
        """
        if self._buffer.can_load():
            batch_id = id_generator.generate_id(type_digit=2, length=8)
            new_batch = ItemBatch(batch_id=batch_id, current_location=Location(self._component_id, self._coordinate))

            if self.event_bus is not None:
                self.event_bus.emit("create_batch", {"id": batch_id})

            log_manager.log(f"Created {new_batch}", f"{self}", sim_time=self.env.now)

            self._buffer.load(new_batch)
            self._current_batch = new_batch # Save instance internally
            # Event for signaling readiness
            self._current_batch.ready_event = self.env.event()

        if self._current_batch.ready_event.triggered:
            # If ready event is triggered, cannot load
            return False
        self._current_batch.add_item(item_id)
        return True

    def _handoff_batch(self):
        """Batch leaves via buffer handoff."""
        yield from self._buffer.handoff()

        if self.event_bus is not None:
            self.event_bus.emit("update_payload", {
                "id": self._current_batch.id,
                "state": BatchState.READY})

        self._current_batch = None # Clear current batch

    def _build_loop(self):
        """
        Wait for batch to be ready to hand it downstream.
        Can also handoff batch if given wait time has been exceeded.
        """
        while True:
            while self._current_batch is None:
                # Wait until a batch exists
                yield self.env.timeout(0.5)

            batch = self._current_batch

            if self.event_bus is not None:
                self.event_bus.emit("batch_builder_building", {"id":self._component_id})

            # Wait for either batch ready event OR timeout
            timeout_event = self.env.timeout(BATCH_MAX_WAIT_TIME)
            yield batch.ready_event | timeout_event

            if self.event_bus is not None:
                self.event_bus.emit("batch_builder_idle", {"id":self._component_id})

            # Handoff batch
            yield self.env.process(self._handoff_batch())