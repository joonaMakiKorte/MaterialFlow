def test_conveyor_one_pallet(env, conveyor_factory, pallet_factory):
    """Load one conveyor with pallet."""
    conveyor = conveyor_factory(1,(0,0),(0,1))
    pallet = pallet_factory(10000000)

    # load pallet at t=0
    def loader(env, conveyor):
        conveyor.load(pallet)
        yield env.timeout(1)

    env.process(loader(env, conveyor))
    env.run(until=5)

    # At the end, pallet should be in last slot
    slots = [p.id if p else None for p in conveyor.slots]
    assert slots == [None, 10000000]
    assert pallet.actual_location.coordinates == (0,1)

def test_conveyor_two_pallets(env, conveyor_factory, pallet_factory):
    """Load one conveyor with two pallets"""
    conveyor = conveyor_factory(1,(0,0),(0,2))
    pallet1 = pallet_factory(10000001)
    pallet2 = pallet_factory(10000002)

    # load pallet at t=0
    def loader(env, conveyor):
        conveyor.load(pallet1)
        yield env.timeout(2)
        # load second pallet after 2 seconds
        conveyor.load(pallet2)

    env.process(loader(env, conveyor))
    env.run(until=5)

    # At the end, first pallet should be in last slot and second pallet in the middle
    slots = [p.id if p else None for p in conveyor.slots]
    assert slots == [None, 10000002, 10000001]
    assert pallet1.actual_location.coordinates == (0, 2)
    assert pallet2.actual_location.coordinates == (0, 1)

def test_two_conveyors_one_pallet(env, conveyor_factory, pallet_factory):
    """Load one conveyor with pallet and transport to linked conveyor."""
    conveyor1 = conveyor_factory(1,(0,0),(0,2),2)
    conveyor2 = conveyor_factory(2,(1,2),(2,2),1)
    conveyor1.connect(conveyor2) # Join conveyors together
    pallet = pallet_factory(10000001)

    # load pallet at t=0
    def loader(env, conveyor):
        conveyor.load(pallet)
        yield env.timeout(1)

    env.process(loader(env, conveyor1))
    env.run(until=8)

    # Make sure pallet reached the end of second conveyor
    slots1 = [p.id if p else None for p in conveyor1.slots]
    slots2 = [p.id if p else None for p in conveyor2.slots]
    assert slots1 == [None, None, None]
    assert slots2 == [None, 10000001]
    assert pallet.actual_location.coordinates == (2,2)
    assert pallet.actual_location.element_name == f"{conveyor2}"

def test_conveyor_with_buffers(env, conveyor_factory, buffer_factory, pallet_factory):
    """Load a pallet on input buffer -> handoff to conveyor -> load on output buffer."""
    # Create elements
    input_buffer = buffer_factory(1, (0,0))
    conveyor = conveyor_factory(1, (1,0), (3,0))
    input_buffer.connect(conveyor) # Join conveyor to buffer output
    output_buffer = buffer_factory(2, (4,0))
    conveyor.connect(output_buffer)
    pallet = pallet_factory(1, (0,0))

    # load pallet at t=0
    def loader(env, buffer):
        buffer.load(pallet)
        yield env.timeout(0)
        yield env.process(buffer.handoff())  # explicitly push to conveyor

    env.process(loader(env, input_buffer))
    env.run(until=8)

    # Assert pallet is on output buffer and other elements are free
    assert pallet.actual_location.coordinates == (4,0)
    assert input_buffer.payload is None
    slots = [p.id if p else None for p in conveyor.slots]
    assert slots == [None, None, None]
    assert output_buffer.payload is not None

def test_one_pallet_depal(env, pallet_factory, depalletizer_factory, conveyor_factory, builder_factory):
    from simulator.core.orders.order import RefillOrder
    """Test depalletizing one order from pallet onto batch builder"""
    # Create depalletizer with input and output conveyors
    pallet = pallet_factory(10000001)
    input_conv = conveyor_factory('conv1', (0,0), (0,2))
    depal = depalletizer_factory('depal1', (0,3))
    output_conv = conveyor_factory('conv2', (1,3), (1,5))
    builder1 = builder_factory('bb1', (0,4))
    item_conv = conveyor_factory('conv3', (0,5), (0,9), 1)
    input_conv.connect(depal)
    depal.connect(output_conv, 'pallet_out')
    depal.connect(builder1, 'item_out')
    builder1.connect(item_conv)

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
    env.run(until=65)

    # Assert depalletizer is empty
    assert depal.can_load()  # payload cleared
    assert depal.payload is None
    assert depal._current_item_id is None and depal.remaining_qty == 0

    # Assert pallet is at output conveyor outfeed
    assert pallet.actual_location.coordinates == output_conv.end
    assert pallet.order is None  # cleared after depal handoff

    # Assert batch builder is empty and item conveyor is full
    assert builder1.payload is None
    slots = [p.id if p else None for p in item_conv.slots]
    assert all(slot is not None for slot in slots)