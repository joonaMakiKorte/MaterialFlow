def test_conveyor_with_buffers(env, conveyor_factory, buffer_factory, pallet_factory):
    """Load a pallet on input buffer -> handoff to conveyor -> load on output buffer."""
    # Create elements
    input_buffer = buffer_factory(1, (0,0))
    conveyor = conveyor_factory(1, (1,0), (3,0))
    input_buffer.connect([conveyor]) # Join conveyor to buffer output
    output_buffer = buffer_factory(2, (4,0))
    conveyor.connect([output_buffer])
    pallet = pallet_factory(1, (0,0))

    # load pallet at t=0
    def loader(env, buffer):
        buffer.load(pallet)
        yield env.timeout(0)
        yield env.process(buffer.handoff(0))  # explicitly push to conveyor

    env.process(loader(env, input_buffer))
    env.run(until=8)

    # Assert pallet is on output buffer and other elements are free
    assert pallet.actual_location.coordinates == (4,0)
    assert input_buffer.payload is None
    slots = [p.pallet_id if p else None for p in conveyor.slots]
    assert slots == [None, None, None]
    assert output_buffer.payload is not None