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
    slots = [p.pallet_id if p else None for p in conveyor.slots]
    assert slots == [None, None, 10000000]
    assert pallet.actual_dest == (0,1)

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
    slots = [p.pallet_id if p else None for p in conveyor.slots]
    assert slots == [None, 10000002, 10000001]
    assert pallet1.actual_dest == (0, 2)
    assert pallet2.actual_dest == (0, 1)

def test_two_conveyors_one_pallet(env, conveyor_factory, pallet_factory):
    """Load one conveyor with pallet and transport to linked conveyor."""
    conveyor1 = conveyor_factory(1,(0,0),(0,2),3,2)
    conveyor2 = conveyor_factory(2,(1,2),(2,2),2,1)
    conveyor1.connect([conveyor2]) # Join conveyors together
    pallet = pallet_factory(10000001)

    # load pallet at t=0
    def loader(env, conveyor):
        conveyor.load(pallet)
        yield env.timeout(1)

    env.process(loader(env, conveyor1))
    env.run(until=8)

    # Make sure pallet reached the end of second conveyor
    slots1 = [p.pallet_id if p else None for p in conveyor1.slots]
    slots2 = [p.pallet_id if p else None for p in conveyor2.slots]
    assert slots1 == [None, None, None]
    assert slots2 == [None, 10000001]
    assert pallet.actual_dest == (2,2)