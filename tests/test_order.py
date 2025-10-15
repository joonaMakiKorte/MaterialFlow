def test_refill_order_gen(env, catalogue, warehouse, inventory_manager, pallet_factory, conveyor_factory, buffer_factory):
    from simulator.core.orders.order import RefillOrder
    """Test placing a refill order to warehouse queue."""
    pallet = pallet_factory(10000000)
    conveyor = conveyor_factory('conv1', (1,0), (3,0))
    input_buffer = buffer_factory('buff1',(0,1))
    output_buffer = buffer_factory('buff2', (0,0))
    warehouse.input_buffer = input_buffer
    warehouse.output_buffer = output_buffer
    output_buffer.connect(conveyor)

    first_item = next(iter(catalogue))
    inventory_manager.place_refill_order(item_id=first_item.item_id, qty_requested=100)

    # Check that order is in the queue
    order = warehouse._order_queue[0][2]
    assert isinstance(order, RefillOrder)

    # load pallet at t=0
    def loader(env, buffer):
        buffer.load(pallet)
        yield env.timeout(0)

    env.process(loader(env, input_buffer))
    env.run(until=10)

    # Make sure order is merged on pallet and order queue is empty
    assert pallet.order.order_id == order.order_id
    assert len(warehouse._order_queue) == 0
    assert pallet.actual_location.coordinates == conveyor.end
