from simulator.database.models import RefillOrder, OpmOrder, Order, OrderStatus

def _seed_sample_orders(db_manager):
    """
    Helper method to seed a consistent set of items and orders for querying tests.
    """
    # Seed items
    db_manager.insert_item(item_id=101, name="Widget A", weight=1.0, category="Prod", volume=1.0, stackable=True)
    db_manager.insert_item(item_id=102, name="Widget B", weight=2.0, category="Prod", volume=2.0, stackable=False)
    db_manager.insert_item(item_id=201, name="Material X", weight=0.5, category="Raw", volume=0.5, stackable=True)
    db_manager.insert_item(item_id=202, name="Material Y", weight=0.7, category="Raw", volume=0.7, stackable=False)

    # Seed Refill Orders
    db_manager.insert_refill_order(order_id=1, order_time=100.0, item_id=201, qty=10)
    db_manager.update_order(order_id=1, status=OrderStatus.COMPLETED,
                            completion_time=150.0)  # Using your generic update

    db_manager.insert_refill_order(order_id=2, order_time=110.0, item_id=201, qty=15)
    db_manager.update_order(order_id=2, status=OrderStatus.IN_PROGRESS)

    db_manager.insert_refill_order(order_id=3, order_time=120.0, item_id=202, qty=20)
    db_manager.update_order(order_id=3, status=OrderStatus.PENDING)

    # Seed OPM Orders
    db_manager.insert_opm_order(order_id=4, order_time=130.0, items={101: 5, 102: 3})
    db_manager.update_order(order_id=4, status=OrderStatus.PENDING)

    db_manager.insert_opm_order(order_id=5, order_time=140.0, items={101: 10})
    db_manager.update_order(order_id=5, status=OrderStatus.COMPLETED, completion_time=180.0)

    db_manager.insert_opm_order(order_id=6, order_time=160.0, items={102: 8})
    db_manager.update_order(order_id=6, status=OrderStatus.IN_PROGRESS)

def test_query_orders_no_filters(db_manager):
    """Tests querying all orders without any filters."""
    _seed_sample_orders(db_manager)
    orders = db_manager.query_orders()
    assert len(orders) == 6
    assert all(isinstance(order, Order) for order in orders)

def test_query_orders_by_id(db_manager):
    """Tests querying an order by its ID."""
    _seed_sample_orders(db_manager)
    order = db_manager.query_orders(id=4)
    assert len(order) == 1
    assert order[0].id == 4
    assert isinstance(order[0], OpmOrder)  # Ensure polymorphism works

def test_query_orders_by_type(db_manager):
    """Tests filtering orders by their type."""
    _seed_sample_orders(db_manager)
    refill_orders = db_manager.query_orders(type='RefillOrder')
    assert len(refill_orders) == 3
    assert all(isinstance(o, RefillOrder) for o in refill_orders)

    opm_orders = db_manager.query_orders(type='OpmOrder')
    assert len(opm_orders) == 3
    assert all(isinstance(o, OpmOrder) for o in opm_orders)

def test_query_orders_by_status(db_manager):
    """Tests filtering orders by their status."""
    _seed_sample_orders(db_manager)
    pending_orders = db_manager.query_orders(status=OrderStatus.PENDING)
    assert len(pending_orders) == 2
    assert {o.id for o in pending_orders} == {3, 4}

    completed_orders = db_manager.query_orders(status=OrderStatus.COMPLETED)
    assert len(completed_orders) == 2
    assert {o.id for o in completed_orders} == {1, 5}

def test_query_orders_by_min_max_order_time(db_manager):
    """Tests filtering by a range of order times."""
    _seed_sample_orders(db_manager)
    orders_after_120 = db_manager.query_orders(min_order_time=125.0)
    assert len(orders_after_120) == 3
    assert {o.id for o in orders_after_120} == {4, 5, 6}

    orders_before_135 = db_manager.query_orders(max_order_time=135.0)
    assert len(orders_before_135) == 4
    assert {o.id for o in orders_before_135} == {1, 2, 3, 4}

    orders_between = db_manager.query_orders(min_order_time=115.0, max_order_time=145.0)
    assert len(orders_between) == 3
    assert {o.id for o in orders_between} == {3, 4, 5}

def test_query_orders_with_ordering(db_manager):
    """Tests sorting query results."""
    _seed_sample_orders(db_manager)
    # Ascending order by order_time
    asc_orders = db_manager.query_orders(order_by='order_time')
    assert [o.id for o in asc_orders] == [1, 2, 3, 4, 5, 6]

    # Descending order by order_time
    desc_orders = db_manager.query_orders(order_by='-order_time')
    assert [o.id for o in desc_orders] == [6, 5, 4, 3, 2, 1]

def test_query_orders_combined_filters_and_ordering(db_manager):
    """Tests combining multiple filters and ordering."""
    _seed_sample_orders(db_manager)
    # Get 1 most recent, pending RefillOrder
    results = db_manager.query_orders(
        type='RefillOrder',
        status=OrderStatus.PENDING,
        order_by='-order_time'
    )
    assert len(results) == 1
    assert results[0].id == 3  # Order 3 is the most recent pending RefillOrder

    # Get all completed orders ordered by completion time
    results = db_manager.query_orders(status=OrderStatus.COMPLETED, order_by='completion_time')
    assert len(results) == 2
    assert [o.id for o in results] == [1, 5]  # Order 1 completed at 150, Order 5 at 180

def test_query_orders_no_results(db_manager):
    """Tests querying for non-existent conditions."""
    _seed_sample_orders(db_manager)
    non_existent_orders = db_manager.query_orders(status=OrderStatus.CANCELLED)
    assert len(non_existent_orders) == 0

    invalid_type_orders = db_manager.query_orders(type='NonExistentType')
    assert len(invalid_type_orders) == 0

def test_query_orders_unknown_filter_key(db_manager):
    """Tests that unknown filter keys are ignored and logged."""
    _seed_sample_orders(db_manager)

    orders = db_manager.query_orders(non_existent_key='abc', status=OrderStatus.PENDING)

    assert len(orders) == 2  # Filter by status should still work