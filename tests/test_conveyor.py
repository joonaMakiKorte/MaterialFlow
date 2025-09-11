import simpy
from simulator.core.components.pallet_conveyor import PalletConveyor
from simulator.core.transportation_units.system_pallet import SystemPallet

def test_conveyor_one_pallet():
    env = simpy.Environment()
    # Create a conveyor with a length of 3
    conveyor = PalletConveyor(env,conveyor_id=1, name="C1", start=(0,0), end=(0,1),num_slots=3,
                              cycle_time=1)
    pallet = SystemPallet(pallet_id=10000000, actual_dest=(0,0))

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

def test_conveyor_two_pallets():
    env = simpy.Environment()
    # Create a conveyor with a length of 3
    conveyor = PalletConveyor(env, conveyor_id=1, name="C1", start=(0, 0), end=(0, 2), num_slots=3,
                              cycle_time=1)
    # Create two transportation_units
    pallet1 = SystemPallet(pallet_id=10000001, actual_dest=(0, 0))
    pallet2 = SystemPallet(pallet_id=10000002, actual_dest=(0, 0))

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

def test_two_conveyors_one_pallet():
    env = simpy.Environment()
    # Create two conveyor and one pallet
    conveyor1 = PalletConveyor(env, conveyor_id=1, name="C1", start=(0, 0), end=(0, 2), num_slots=3, cycle_time=2)
    conveyor2 = PalletConveyor(env, conveyor_id=2, name="C2", start=(1, 2), end=(2, 2), num_slots=2, cycle_time=1)
    conveyor1.connect([conveyor2]) # Join conveyors together

    pallet = SystemPallet(pallet_id=10000001, actual_dest=(0, 0))

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