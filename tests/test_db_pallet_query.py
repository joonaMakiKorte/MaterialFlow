def _seed_test_pallets(db_manager):
    """Helper method for seeding the pallets table."""
    db_manager.insert_pallet(pallet_id=101, location='Warehouse', sim_time=0)
    db_manager.insert_pallet(pallet_id=102, location='Warehouse', sim_time=10)
    db_manager.insert_pallet(pallet_id=103, location='ItemWarehouse', sim_time=15)
    db_manager.insert_pallet(pallet_id=104, location='Buffer', sim_time=20)

    # Make 2 pallets be non-stored
    db_manager.update_pallet(pallet_id=103, sim_time=20, stored=False, order_id=101)
    db_manager.update_pallet(pallet_id=104, sim_time=25, stored=False, order_id=101)


def test_query_pallets_no_filters(db_manager):
    """
    Tests that querying with no filters returns all pallets, sorted by the default (ID asc).
    """
    _seed_test_pallets(db_manager)

    results = db_manager.query_pallets()

    assert len(results) == 4
    # Check default ordering is by ID ascending
    assert [p.id for p in results] == [101, 102, 103, 104]

def test_query_pallets_filter_by_stored(db_manager):
    """
    Tests filtering by the boolean 'stored' field.
    """
    _seed_test_pallets(db_manager)

    # Query for active (not stored) pallets
    active_pallets = db_manager.query_pallets(stored=False)
    assert len(active_pallets) == 2
    assert all(not p.stored for p in active_pallets)
    # Verify the IDs to be sure
    assert {p.id for p in active_pallets} == {103, 104}

    # Query for stored pallets
    stored_pallets = db_manager.query_pallets(stored=True)
    assert len(stored_pallets) == 2
    assert all(p.stored for p in stored_pallets)
    assert {p.id for p in stored_pallets} == {101, 102}


def test_query_pallets_descending_sort(db_manager):
    """
    Tests the descending sort order.
    """
    _seed_test_pallets(db_manager)

    # Sort by last_updated_sim_time in descending order
    results = db_manager.query_pallets(order_by='-last_updated_sim_time')

    assert len(results) == 4
    # Check that the list is correctly sorted from newest to oldest
    assert [p.id for p in results] == [104,103,102,101]
    assert results[0].last_updated_sim_time == 25
    assert results[3].last_updated_sim_time == 0


def test_query_pallets_ascending_sort(db_manager):
    """
    Tests the ascending sort order.
    """
    _seed_test_pallets(db_manager)

    results = db_manager.query_pallets(order_by='last_updated_sim_time')

    assert len(results) == 4
    # Check that the list is correctly sorted from oldest to newest
    assert [p.id for p in results] == [101,102,103,104]
    assert results[0].last_updated_sim_time == 0
    assert results[2].last_updated_sim_time == 20


def test_query_pallets_combined_filter_and_sort(db_manager):
    """
    Tests that filtering and sorting can be applied simultaneously.
    """
    _seed_test_pallets(db_manager)

    # Get active pallets with a specific order_id, sorted by time
    results = db_manager.query_pallets(
        stored=False,
        order_id=101,
        order_by='-last_updated_sim_time'
    )

    assert len(results) == 2
    assert [p.id for p in results] == [104,103]
    assert all(not p.stored and p.order_id == 101 for p in results)


def test_query_pallets_no_results(db_manager):
    """
    Tests that a query with filters that match no records returns an empty list.
    """
    _seed_test_pallets(db_manager)

    results = db_manager.query_pallets(location='NonExistentLocation')

    assert isinstance(results, list)
    assert len(results) == 0


def test_query_pallets_ignores_unknown_filter_key(db_manager):
    """
    Tests that the query method ignores filter keys that do not match a column
    and returns an unfiltered list.
    """
    _seed_test_pallets(db_manager)

    # 'color' is not a valid attribute on the Pallet model
    results = db_manager.query_pallets(color='blue')

    # It should ignore the bad filter and return all pallets
    assert len(results) == 4