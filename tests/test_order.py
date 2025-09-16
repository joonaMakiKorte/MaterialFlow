from simulator.core.orders.order import RefillOrder

def test_refill_order_gen(env, catalogue, warehouse, order_service, pallet_factory):
    """Test placing a refill order to warehouse queue."""
    pallet = pallet_factory(10000000)

    first_item_id = next(iter(catalogue.items.values())).item_id
    order_service.place_refill_order(item_id=first_item_id, qty_requested=100)

    # Check that order is in the queue
    order = warehouse._order_queue[0][1]
    assert isinstance(warehouse._order_queue[0][1], RefillOrder)

    # load pallet at t=0
    def loader(env, buffer):
        buffer.load(pallet)
        yield env.timeout(0)

    env.process(loader(env, warehouse.buffer))
    env.run(until=5)

    # Make sure order is merged on pallet and order queue is empty
    assert pallet.order.order_id == order.order_id
    assert len(warehouse._order_queue) == 0
