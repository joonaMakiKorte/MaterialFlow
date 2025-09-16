import pytest
import simpy
from simulator.core.items.catalogue import Catalogue
from simulator.core.components.pallet_conveyor import PalletConveyor
from simulator.core.transportation_units.system_pallet import SystemPallet
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.orders.order_service import OrderService
from simulator.core.stock.warehouse import Warehouse

@pytest.fixture
def env():
    return simpy.Environment()

@pytest.fixture
def catalogue():
    return Catalogue()

@pytest.fixture
def conveyor_factory(env):
    """Create conveyor with 3 slots and cycle time of 1."""
    def _factory(conveyor_id, start, end, num_slots=3, cycle_time=1):
        return PalletConveyor(
            env,
            conveyor_id=conveyor_id,
            name=f"C{conveyor_id}",
            start=start,
            end=end,
            num_slots=num_slots,
            cycle_time=cycle_time
        )
    return _factory

@pytest.fixture
def buffer_factory(env):
    """Factory to create payload buffers """
    def _factory(buffer_id, coordinate, cycle_time=1):
        return PayloadBuffer(
            env,
            buffer_id=buffer_id,
            name=f"B{buffer_id}",
            coordinate=coordinate,
            cycle_time=cycle_time
        )
    return _factory

@pytest.fixture
def pallet_factory():
    """Create pallet with default destination (0,0)."""
    def _factory(pallet_id, dest=(0,0)):
        return SystemPallet(pallet_id=pallet_id, actual_dest=dest)
    return _factory

@pytest.fixture
def warehouse(env, buffer_factory):
    return Warehouse(
        env,
        warehouse_id=1,
        name=f"Warehouse",
        buffer=buffer_factory(buffer_id=1,coordinate=(0,0)),
        process_time=1
    )

@pytest.fixture
def order_service(env, catalogue, warehouse):
    """Initialize order service with warehouse"""
    return OrderService(
        env,
        catalogue,
        warehouse
    )