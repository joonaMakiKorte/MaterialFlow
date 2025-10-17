import pytest
import simpy
import json
from simulator.core.factory.id_gen import IDGenerator
from simulator.core.items.catalogue import Catalogue
from simulator.core.components.payload_conveyor import PayloadConveyor
from simulator.core.transportation_units.system_pallet import SystemPallet, Location
from simulator.core.transportation_units.item_batch import ItemBatch
from simulator.core.components.payload_buffer import PayloadBuffer
from simulator.core.components.depalletizer import Depalletizer
from simulator.core.orders.inventory_manager import InventoryManager
from simulator.core.components.batch_builder import BatchBuilder
from simulator.core.stock.warehouse import Warehouse
from simulator.core.stock.item_warehouse import ItemWarehouse
from simulator.core.routing.factory_graph import FactoryGraph

@pytest.fixture
def env():
    return simpy.Environment()

@pytest.fixture
def mock_items_json(tmp_path):
    """Fixture that creates a temporary mock items.json file and returns its path."""
    mock_items = [
        {
            "item_id": 1001,
            "name": "Apple",
            "weight": 0.2,
            "category": "Fruit",
            "volume": 0.1,
            "stackable": True,
        },
        {
            "item_id": 1002,
            "name": "Cheddar Cheese Block",
            "weight": 0.5,
            "category": "Dairy",
            "volume": 0.5,
            "stackable": True,
        },
    ]

    json_path = tmp_path / "items.json"
    with open(json_path, "w") as f:
        json.dump(mock_items, f)

    return json_path

@pytest.fixture
def mock_factory_json(tmp_path):
    """
    Fixture that creates a temporary mock factory_init.json file and returns its path.
    The mock layout is simplified for testing purposes only.
    """
    mock_factory = {
        "components" : [
            {
                "id": "wh_buff_out",
                "type": "PayloadBuffer",
                "coordinate": [0,0]
            },
            {
                "id": "wh_buff_in",
                "type": "PayloadBuffer",
                "coordinate": [1,0]
            },
            {
                "id": "pallet_conv1",
                "type": "PayloadConveyor",
                "start": [0,1],
                "end": [0,4]
            }
        ],
        "connections" : [
            {
                "from" : "wh_buff_out",
                "to" : "pallet_conv1",
                "port" : "out"
            }
        ],
        "stock" : {
            "warehouse" : {
                "input_buffer": "wh_buff_in",
                "output_buffer": "wh_buff_out"
            }
        }

    }

    json_path = tmp_path / "factory_init.json"
    with open(json_path, "w") as f:
        json.dump(mock_factory, f)

    return json_path

@pytest.fixture
def catalogue(mock_items_json):
    return Catalogue(str(mock_items_json))

@pytest.fixture
def id_gen():
    return IDGenerator()

@pytest.fixture
def factory_graph():
    return FactoryGraph()

@pytest.fixture
def conveyor_factory(env):
    """Create conveyor with 3 slots and cycle time of 1."""
    def _factory(conveyor_id, start, end, cycle_time=1):
        conv = PayloadConveyor(
            env=env,
            conveyor_id=conveyor_id,
            start=start,
            end=end,
            cycle_time=cycle_time
        )
        return conv
    return _factory

@pytest.fixture
def buffer_factory(env):
    """Factory to create payload buffers."""
    def _factory(buffer_id, coordinate, process_time=1):
        buffer = PayloadBuffer(
            env=env,
            buffer_id=buffer_id,
            coordinate=coordinate,
            process_time=process_time
        )
        return buffer
    return _factory

@pytest.fixture
def depalletizer_factory(env):
    """Factory to create depalletizers"""
    def _factory(depalletizer_id, coordinate, pallet_process_time = 1, item_process_time = 1, start_delay = 1):
        depal = Depalletizer(
            env=env,
            depalletizer_id=depalletizer_id,
            coordinate=coordinate,
            pallet_process_time=pallet_process_time,
            item_process_time=item_process_time,
            start_delay=start_delay
        )
        return depal
    return _factory

@pytest.fixture
def builder_factory(env, id_gen):
    def _factory(builder_id, coordinate, batch_process_time = 1):
        batch_builder = BatchBuilder(
            env=env,
            id_gen=id_gen,
            builder_id=builder_id,
            coordinate=coordinate,
            batch_process_time=batch_process_time
        )
        return batch_builder
    return _factory

@pytest.fixture
def pallet_factory():
    """Create pallet with default destination (0,0)."""
    def _factory(pallet_id, dest=(0,0)):
        return SystemPallet(
            pallet_id=pallet_id,
            actual_location=Location("",dest))
    return _factory

@pytest.fixture
def batch_factory():
    """Create batch with default destination (0,0) and load 10 counts of requested item id."""
    def _factory(batch_id, item_id, dest=(0,0)):
        batch = ItemBatch(
            batch_id=batch_id,
            actual_location=Location("",dest)
        )
        batch._items = {item_id : 10}
        batch._item_count = 10
        return batch
    return _factory

@pytest.fixture
def warehouse(env):
     return Warehouse(
         env=env,
         order_process_time=1,
         pallet_process_time=1
     )

@pytest.fixture
def item_warehouse(env):
    return ItemWarehouse(
        env=env,
        item_process_time=1,
        batch_process_time=1
    )

@pytest.fixture
def inventory_manager(env, id_gen, catalogue, warehouse):
    """Initialize order service with warehouse"""
    return InventoryManager(
        id_gen=id_gen,
        catalogue=catalogue,
        warehouse=warehouse
    )