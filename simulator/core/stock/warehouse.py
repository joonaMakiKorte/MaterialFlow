from simulator.core.orders.order import RefillOrder, OrderStatus
from simulator.core.stock.stock import Stock
from simulator.core.components.payload_buffer import PayloadBuffer
import simpy

class Warehouse(Stock):
    """
    Manages item refills to ItemWarehouse (RefillOrder).
    Contains an I/O component (PayloadBuffer) where orders get merged on pallets.

    Additional Attributes
    ----------
    buffer : PayloadBuffer
        I/O component where orders get merged on pallets.
    process_time : float
        Time to process an order
    """
    def __init__(self, env: simpy.Environment, warehouse_id: int, buffer: PayloadBuffer, process_time: float):
        super().__init__(env, warehouse_id)
        self._buffer = buffer
        self._process_time = process_time

    # ----------
    # Properties
    # ----------

    @property
    def buffer(self) -> PayloadBuffer:
        return self._buffer

    @property
    def process_time(self) -> float:
        return self._process_time

    # ----------
    #   Logic
    # ----------

    def process_order(self, order: RefillOrder):
        """Process order by merging it on the pallet on buffer."""
        self.buffer.payload.order = order
        print(f"[{self.env.now}] Warehouse: Processed order {order}")
        # TODO assign a new destination for the pallet
        order.status = OrderStatus.IN_PROGRESS # Update order status to pending
        yield self.env.timeout(self.process_time)

    def run(self):
        """Main order processing loop"""
        while True:
            self.buffer.on_load_event = self.env.event()
            pallet = yield self.buffer.on_load_event  # wait for pallet

            print(f"[{self.env.now}] Warehouse: Buffer has {pallet}")

            if self._has_orders():
                order = self._next_order()
                print(f"[{self.env.now}] {self}: Processing order {order}")

                # run the order process
                yield self.env.process(self.process_order(order))

                # trigger buffer handoff
                #yield self.env.process(self.buffer.handoff(0))
            else:
                print(f"[{self.env.now}] Warehouse: No orders in queue!")

