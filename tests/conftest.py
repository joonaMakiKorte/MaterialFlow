import pytest
import simpy
from simulator.core.items.catalogue import Catalogue
from simulator.core.components.pallet_conveyor import PalletConveyor
from simulator.core.transportation_units.system_pallet import SystemPallet, Location
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.depalletizer import Depalletizer
from simulator.core.orders.inventory_manager import InventoryManager
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
        conv = PalletConveyor(
            conveyor_id=conveyor_id,
            start=start,
            end=end,
            num_slots=num_slots,
            cycle_time=cycle_time
        )
        conv.inject_env(env)
        return conv
    return _factory

@pytest.fixture
def buffer_factory(env):
    """Factory to create payload buffers."""
    def _factory(buffer_id, coordinate, process_time=1):
        buffer = PayloadBuffer(
            buffer_id=buffer_id,
            coordinate=coordinate,
            process_time=process_time
        )
        buffer.inject_env(env)
        return buffer
    return _factory

@pytest.fixture
def depalletizer_factory(env):
    """Factory to create depalletizers"""
    def _factory(depalletizer_id, coordinate, item_cycle_time=1, pallet_unload_time=1):
        depal = Depalletizer(
            depalletizer_id=depalletizer_id,
            coordinate=coordinate,
            item_process_time=item_cycle_time,
            pallet_unload_time=pallet_unload_time
        )
        depal.inject_env(env)
        return depal
    return _factory

@pytest.fixture
def pallet_factory():
    """Create pallet with default destination (0,0)."""
    def _factory(pallet_id, dest=(0,0)):
        return SystemPallet(pallet_id=pallet_id, actual_location=Location("",dest))
    return _factory

@pytest.fixture
def warehouse(env, buffer_factory):
     whouse = Warehouse(warehouse_id=1, process_time=1)
     whouse.inject_env(env)
     return whouse

@pytest.fixture
def order_service(env, catalogue, warehouse):
    """Initialize order service with warehouse"""
    return InventoryManager(
        env,
        catalogue,
        warehouse
    )