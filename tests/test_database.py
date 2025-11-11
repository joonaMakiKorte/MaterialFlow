from sqlalchemy import create_engine, inspect
from simulator.database.models import Item, Pallet, RefillOrder, OpmOrder, Order, OrderStatus

def test_setup_database(db_manager):
    """
    Tests if the setup_database method correctly creates all expected tables.
    """
    inspector = inspect(db_manager.engine)
    tables = inspector.get_table_names()

    assert "items" in tables
    assert "pallets" in tables
    assert "orders" in tables
    assert "refill_orders" in tables
    assert "opm_orders" in tables
    assert "opm_order_items" in tables

def test_insert_item(db_manager):
    """
    Tests inserting a new item and ensures it's stored correctly.
    Also tests that duplicate insertions are ignored.
    """
    item_data = {
        "item_id": 101, "name": "Test Widget", "weight": 5.5,
        "category": "Widgets", "volume": 1.2, "stackable": True
    }

    db_manager.insert_item(**item_data)
    db_manager.insert_item(**item_data)  # Insert again to test idempotency

    # Assert
    with db_manager.Session() as session:
        item = session.get(Item, 101)
        assert item is not None
        assert item.name == "Test Widget"
        assert item.weight == 5.5
        assert item.stackable is True
        # Check that there's only one item
        assert session.query(Item).count() == 1

def test_insert_pallet(db_manager):
    """Tests inserting a new pallet."""
    db_manager.insert_pallet(
        pallet_id=1, location="A1", destination="B2",
        order_id=None, sim_time=123.45
    )

    # Assert
    with db_manager.Session() as session:
        pallet = session.get(Pallet, 1)
        assert pallet is not None
        assert pallet.location == "A1"
        assert pallet.destination == "B2"
        assert pallet.order_id is None
        assert pallet.last_updated_sim_time == 123.45

def test_update_pallet(db_manager):
    """Tests updating an existing pallet's attributes."""
    db_manager.insert_pallet(
        pallet_id=1, location="A1", destination=None,
        order_id=None, sim_time=100.0
    )

    db_manager.update_pallet(
        pallet_id=1, sim_time=200.5,
        location="C3", destination="D4", unknown_attr="ignore"
    )

    with db_manager.Session() as session:
        pallet = session.get(Pallet, 1)
        assert pallet.location == "C3"
        assert pallet.destination == "D4"
        assert pallet.last_updated_sim_time == 200.5

def test_insert_refill_order(db_manager):
    """Tests inserting a RefillOrder, which involves two tables."""
    db_manager.insert_item(
        item_id=202, name="Refill Item", weight=1,
        category="Supplies", volume=1, stackable=False
    )

    db_manager.insert_refill_order(
        order_id=5001, order_time=300.0, item_id=202, qty=50
    )

    with db_manager.Session() as session:
        # Check the specific RefillOrder table
        refill_order = session.get(RefillOrder, 5001)
        assert refill_order is not None
        assert refill_order.item_id == 202
        assert refill_order.qty == 50

        # Check the base Order table to ensure polymorphism works
        base_order = session.get(Order, 5001)
        assert base_order is not None
        assert base_order.order_time == 300.0
        assert base_order.status == OrderStatus.PENDING

def test_insert_opm_order(db_manager):
    """Tests inserting an OpmOrder with its item dictionary."""
    db_manager.insert_item(item_id=303, name="OPM Item A", weight=1, category="A", volume=1, stackable=True)
    db_manager.insert_item(item_id=304, name="OPM Item B", weight=2, category="B", volume=2, stackable=False)

    requested_items = {303: 10, 304: 20}

    db_manager.insert_opm_order(order_id=6001, order_time=400.0, items=requested_items)

    with db_manager.Session() as session:
        opm_order = session.get(OpmOrder, 6001)
        assert opm_order is not None
        assert opm_order.order_time == 400.0

        # The association proxy should make the .items attribute work like a dict
        assert opm_order.items == requested_items

def test_update_order(db_manager):
    """Tests updating an order's status."""
    db_manager.insert_item(item_id=202, name="Refill Item", weight=1, category="S", volume=1, stackable=False)
    db_manager.insert_refill_order(order_id=5001, order_time=300.0, item_id=202, qty=50)

    db_manager.update_order(order_id=5001, status=OrderStatus.IN_PROGRESS)

    with db_manager.Session() as session:
        order = session.get(Order, 5001)
        assert order is not None
        assert order.status == OrderStatus.IN_PROGRESS

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

def test_query_orders_by_item_id(db_manager):
    """Tests filtering RefillOrders by an item_id, requiring a JOIN."""
    _seed_sample_orders(db_manager)
    orders_for_item_201 = db_manager.query_orders(item_id=201)
    assert len(orders_for_item_201) == 2
    assert {o.id for o in orders_for_item_201} == {1, 2}
    assert all(isinstance(o, RefillOrder) for o in orders_for_item_201)  # Check if they are RefillOrders

    # Test item not associated with any refill orders
    orders_for_item_101 = db_manager.query_orders(item_id=101)
    assert len(orders_for_item_101) == 0  # OpmOrder has item 101, but filter is for RefillOrder's item_id

def test_query_orders_with_ordering(db_manager):
    """Tests sorting query results."""
    _seed_sample_orders(db_manager)
    # Ascending order by order_time
    asc_orders = db_manager.query_orders(order_by='order_time')
    assert [o.id for o in asc_orders] == [1, 2, 3, 4, 5, 6]

    # Descending order by order_time
    desc_orders = db_manager.query_orders(order_by='-order_time')
    assert [o.id for o in desc_orders] == [6, 5, 4, 3, 2, 1]

def test_query_orders_with_limit(db_manager):
    """Tests limiting the number of query results."""
    _seed_sample_orders(db_manager)
    limited_orders = db_manager.query_orders(limit=3, order_by='order_time')
    assert len(limited_orders) == 3
    assert [o.id for o in limited_orders] == [1, 2, 3]

def test_query_orders_combined_filters_and_ordering(db_manager):
    """Tests combining multiple filters and ordering."""
    _seed_sample_orders(db_manager)
    # Get 1 most recent, pending RefillOrder
    results = db_manager.query_orders(
        type='RefillOrder',
        status=OrderStatus.PENDING,
        order_by='-order_time',
        limit=1
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