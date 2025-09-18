from simulator.core.orders.order import RefillOrder

def test_one_pallet_depal(env, pallet_factory, depalletizer_factory, conveyor_factory):
    """Test depalletizing one order from pallet"""
    # Create depalletizer with input and output conveyors
    pallet = pallet_factory(10000001)
    input_conv = conveyor_factory(1, (0,0), (0,2))
    depal = depalletizer_factory(1, (0,3))
    output_conv = conveyor_factory(2, (0,4), (0,6))
    input_conv.connect(depal)
    depal.connect(output_conv)

    # Create
    test_order = RefillOrder(order_id=1, item_id=1, qty=50)
    pallet.merge_order(test_order, "depalletizer")
    pallet.requested_dest.specify(element_id=1)

    # load pallet at t=0
    def loader(env, conveyor):
        conveyor.load(pallet)
        yield env.timeout(0)

    env.process(loader(env, input_conv))
    env.run(until=5)

    # Assert pallet is being processed in depal
    assert pallet.actual_location.coordinates == depal.coordinate
    assert depal.current_item_id == test_order.item_id
    # There should be 40+ items left at this point
    assert depal.remaining_qty > 40
    assert depal.current_process_time_left() > 40.0

    # Run until pallet should have finished unloading
    env.run(until=60)

    # Assert depalletizer is empty
    assert depal.can_load()  # payload cleared
    assert depal._payload is None
    assert depal._current_item_id is None and depal.remaining_qty == 0

    # Assert pallet is at output conveyor outfeed
    assert pallet.actual_location.coordinates == output_conv.end
    assert pallet.order is None  # cleared after depal handoff
