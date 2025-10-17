def test_refill_order_gen(env, catalogue, warehouse, inventory_manager):
    from simulator.core.orders.order import RefillOrder
    """Test placing a refill order to warehouse queue through inventory manager."""
    first_item = next(iter(catalogue))
    inventory_manager.place_refill_order(item_id=first_item.item_id, qty_requested=100)

    # Check that order is in the queue
    order = warehouse._order_queue[0][2]
    assert isinstance(order, RefillOrder)

