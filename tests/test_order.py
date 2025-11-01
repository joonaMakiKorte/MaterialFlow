from simulator.core.orders.order import RefillOrder, OpmOrder

def test_refill_order_gen(env, catalogue, warehouse, inventory_manager):
    """Test placing a refill order to warehouse queue through inventory manager."""
    first_item = next(iter(catalogue))
    inventory_manager.place_refill_order(item_id=first_item.item_id, qty_requested=100)

    # Check that order is in the queue
    order = warehouse._order_queue[0][2]
    assert isinstance(order, RefillOrder)

def test_opm_order_gen(env, catalogue, item_warehouse, inventory_manager):
    """Test placing an opm order to item warehouse queue through inventory manager."""
    first_item = next(iter(catalogue))
    order_dict = {first_item.item_id : 100} # Order 100 pieces of the item
    inventory_manager.place_opm_order(order_dict)

    # Check that order is in the queue
    order = item_warehouse._order_queue[0][2]
    assert isinstance(order, OpmOrder)

def test_auto_refill_order_gen(env, catalogue, item_warehouse, warehouse, inventory_manager, buffer_factory):
    """Test placing an opm order and run simulation until inventory manager has placed an automatic refill"""
    first_item = next(iter(catalogue))
    order_dict = {first_item.item_id: 100}  # Order 100 pieces of the item
    inventory_manager.place_opm_order(order_dict)

    # Attach input and output buffers for warehouse for the processes to work
    input_buffer = buffer_factory('buff_in', coordinate=(1, 1))
    output_buffer = buffer_factory('buff_out', coordinate=(0, 0))
    warehouse.input_buffer = input_buffer
    warehouse.output_buffer = output_buffer

    def generator():
        yield env.timeout(0)

    env.process(generator())
    env.run(10)

    # Item warehouse request queue should be empty
    assert len(item_warehouse.requested_items_queue.items) == 0

    # There should be a refill order in warehouse queue
    assert warehouse.order_count == 1
    order = warehouse._order_queue[0][2]
    assert isinstance(order, RefillOrder)
    assert order.qty == 100

def test_order_priority_queue(env, warehouse):
    """Test placing orders to queue with different priorities"""
    # Create 3 mock orders
    order1 = RefillOrder(order_id=1, order_time=1, item_id=1, qty=10)
    order2 = RefillOrder(order_id=2, order_time=1, item_id=10, qty=12)
    order3 = RefillOrder(order_id=5, order_time=1, item_id=100, qty=100)

    # Place orders with different priorities
    warehouse.place_order(order1, priority=10)
    warehouse.place_order(order2, priority=0)
    warehouse.place_order(order3, priority=100)

    # Asset the orders are in order 2, 1, 3
    assert warehouse.order_count == 3
    assert warehouse._order_queue[0][2] == order2
    assert warehouse._order_queue[1][2] == order1
    assert warehouse._order_queue[2][2] == order3


