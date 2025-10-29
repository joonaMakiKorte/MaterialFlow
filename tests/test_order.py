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
