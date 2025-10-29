def test_warehouse_input(env, warehouse, buffer_factory, pallet_factory):
    """Test pallet storage in warehouse"""
    input_buffer = buffer_factory('buff1', (0,0))
    warehouse.input_buffer = input_buffer
    pallet = pallet_factory('1001')

    # load pallet at 0
    def loader(env, buffer):
        buffer.load(pallet)
        yield env.timeout(0)

    env.process(loader(env, input_buffer))
    env.run(until=5)

    # Assert the buffer is empty and warehouse has one pallet in stock
    assert input_buffer._payload is None
    assert warehouse._pallet_count == 1

def test_warehouse_output(env, warehouse, buffer_factory, pallet_factory):
    from simulator.core.orders.order import RefillOrder
    """Place a mock order in warehouse queue and process it."""
    input_buffer = buffer_factory('buff_in', coordinate=(1,1))
    output_buffer = buffer_factory('buff_out', coordinate=(0,0))
    warehouse.input_buffer = input_buffer
    warehouse.output_buffer = output_buffer
    pallet = pallet_factory('1001')

    # Place order in queue
    order = RefillOrder(order_id=1, order_time=0, item_id=1, qty=1)
    warehouse.place_order(order, priority=10)

    # Place pallet in warehouse input buffer
    def loader():
        input_buffer.load(pallet)
        yield env.timeout(0)

    env.process(loader())
    env.run(until=10)

    # Make sure order is merged on pallet at output buffer and order queue is empty
    assert pallet.order.id == order.id
    assert len(warehouse._order_queue) == 0
    assert pallet.actual_location.coordinates == output_buffer.coordinate

def test_itemwarehouse_input(env, item_warehouse, buffer_factory, batch_factory):
    """Test batch storage in item warehouse"""
    input_buffer = buffer_factory('buff1', (0,0))
    item_warehouse.inject_input_buffer(input_buffer)
    batch = batch_factory('1001', item_id=1000)

    # load batch at 0
    def loader():
        input_buffer.load(batch)
        yield env.timeout(0)

    env.process(loader())
    env.run(until=5)

    # Assert the buffer is empty and item warehouse has the items
    assert input_buffer._payload is None
    assert item_warehouse._item_count == 10 # 10 is default item count for batches
    assert item_warehouse._item_stock.get(1000) == 10

def test_itemwarehouse_two_inputs(env, item_warehouse, buffer_factory, batch_factory):
    """Test loading two batches on two item_warehouse input buffers"""
    input_buffer1 = buffer_factory('buff1', (0,0))
    input_buffer2 = buffer_factory('buff2', (1,0))
    item_warehouse.inject_input_buffer(input_buffer1)
    item_warehouse.inject_input_buffer(input_buffer2)
    batch1 = batch_factory('1001', item_id=1000)
    batch2 = batch_factory('1002', item_id=1010)

    # load two batches with a small delay
    def loader():
        input_buffer1.load(batch1)
        yield env.timeout(1)
        input_buffer2.load(batch2)

    env.process(loader())
    env.run(until=6)

    # Assert the buffers are empty and item warehouse has the items
    assert input_buffer1._payload is None and input_buffer2._payload is None
    assert item_warehouse._item_count == 20 # 10 is default item count for batches
    assert item_warehouse._item_stock.get(1000) == 10 and item_warehouse._item_stock.get(1010) == 10

