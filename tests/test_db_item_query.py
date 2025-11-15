from simulator.database.models import Item

def _create_test_items(db_manager):
    """Creates a standard set of items for testing."""
    items_to_add = [
        Item(id=1, name='CPU', weight=0.5, category='Electronics', volume=0.1, stackable=True),
        Item(id=2, name='Motherboard', weight=1.5, category='Electronics', volume=0.8, stackable=False),
        Item(id=3, name='Wooden Crate', weight=10.0, category='Packaging', volume=5.0, stackable=True),
        Item(id=4, name='Metal Screws', weight=2.0, category='Hardware', volume=0.2, stackable=True),
        Item(id=5, name='Plastic Wrap', weight=3.0, category='Packaging', volume=1.5, stackable=False),
    ]
    with db_manager.Session() as session:
        session.add_all(items_to_add)
        session.commit()

def test_insert_item_success(db_manager):
    """
    Tests that a new item can be successfully inserted into the database.
    """
    db_manager.insert_item(
        item_id=10, name='Test Item', weight=9.9,
        category='Test Category', volume=1.1, stackable=True
    )

    with db_manager.Session() as session:
        item = session.get(Item, 10)
        assert item is not None
        assert item.name == 'Test Item'
        assert item.category == 'Test Category'
        assert item.stackable is True


def test_insert_item_skips_duplicate(db_manager):
    """
    Tests that attempting to insert an item with an existing ID is skipped
    without raising an error or altering the existing record.
    """
    # Insert initial item
    db_manager.insert_item(
        item_id=20, name='Original Item', weight=1.0,
        category='Original', volume=1.0, stackable=False
    )

    # Attempt to insert a duplicate with different data
    db_manager.insert_item(
        item_id=20, name='Duplicate Item', weight=2.0,
        category='Duplicate', volume=2.0, stackable=True
    )

    with db_manager.Session() as session:
        item = session.get(Item, 20)
        # Verify the original item was not changed
        assert item.name == 'Original Item'
        assert item.category == 'Original'
        # Verify there is only one item with that ID
        count = session.query(Item).filter(Item.id == 20).count()
        assert count == 1


# --- Tests for get_all_item_categories ---

def test_get_all_item_categories_success(db_manager):
    """
    Tests that a unique, sorted list of categories is returned.
    """
    _create_test_items(db_manager)

    categories = db_manager.get_all_item_categories()

    assert isinstance(categories, list)
    # Should be sorted alphabetically and unique
    assert categories == ['Electronics', 'Hardware', 'Packaging']


def test_get_all_item_categories_empty_db(db_manager):
    """
    Tests that an empty list is returned when there are no items in the database.
    """
    categories = db_manager.get_all_item_categories()
    assert categories == []

def test_query_items_no_filters(db_manager):
    """
    Tests that querying with no arguments returns all items, sorted by ID.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items()

    assert len(items) == 5
    # Default sort is by ID ascending
    assert [item.id for item in items] == [1, 2, 3, 4, 5]


def test_query_items_filter_by_category(db_manager):
    """
    Tests filtering by an exact match on the 'category' field.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items(category='Packaging')

    assert len(items) == 2
    assert all(item.category == 'Packaging' for item in items)
    assert {item.id for item in items} == {3, 5}


def test_query_items_filter_by_stackable(db_manager):
    """
    Tests filtering by a boolean 'stackable' field.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items(stackable=True)

    assert len(items) == 3
    assert all(item.stackable is True for item in items)
    assert {item.id for item in items} == {1, 3, 4}


def test_query_items_name_contains_filter(db_manager):
    """
    Tests the case-insensitive 'name_contains' filter.
    """
    _create_test_items(db_manager)

    # Test a simple substring
    items = db_manager.query_items(name_contains='board')
    assert len(items) == 1
    assert items[0].name == 'Motherboard'

    # Test case-insensitivity
    items_case = db_manager.query_items(name_contains='wOoDeN')
    assert len(items_case) == 1
    assert items_case[0].id == 3


def test_query_items_descending_sort(db_manager):
    """
    Tests sorting by a column in descending order.
    """
    _create_test_items(db_manager)

    # Sort by weight, heaviest first
    items = db_manager.query_items(order_by='-weight')

    assert len(items) == 5
    assert [item.id for item in items] == [3, 5, 4, 2, 1]
    assert items[0].weight == 10.0
    assert items[4].weight == 0.5


def test_query_items_combined_filter_and_sort(db_manager):
    """
    Tests that filtering and sorting can be applied together.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items(category='Electronics', order_by='-weight')

    assert len(items) == 2
    # Motherboard (1.5) is heavier than CPU (0.5)
    assert [item.id for item in items] == [2, 1]


def test_query_items_no_results(db_manager):
    """
    Tests that a query matching no items returns an empty list.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items(category='NonExistentCategory')

    assert isinstance(items, list)
    assert len(items) == 0


def test_query_items_ignores_unknown_filter(db_manager):
    """
    Tests that an unknown filter key is ignored, returning all results.
    """
    _create_test_items(db_manager)

    items = db_manager.query_items(color='red', order_by='id')

    # Should ignore 'color' and just return all items, sorted by id
    assert len(items) == 5
    assert [item.id for item in items] == [1, 2, 3, 4, 5]