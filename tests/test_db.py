from sqlalchemy import inspect
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
        pallet_id=1, location="A1", sim_time=123.45
    )

    # Assert
    with db_manager.Session() as session:
        pallet = session.get(Pallet, 1)
        assert pallet is not None
        assert pallet.location == "A1"
        assert pallet.destination is None
        assert pallet.order_id is None
        assert pallet.stored == True
        assert pallet.last_updated_sim_time == 123.45

def test_update_pallet(db_manager):
    """Tests updating an existing pallet's attributes."""
    db_manager.insert_pallet(
        pallet_id=1, location="A1", sim_time=100.0
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