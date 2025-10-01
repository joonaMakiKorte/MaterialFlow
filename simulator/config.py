"""Simulation-wide constants"""

# -----------
# Data paths
# -----------

ITEM_JSON = "items.json"
FACTORY_JSON = "factory_init.json"

# ---------------------------------------------------
# Operation times for elements in simulation units
# Simulation time unit = 1 second in simulation world
# ---------------------------------------------------

TIME_SCALE = 0.3 # seconds per simulation unit

# CONVEYOR
CONVEYOR_CYCLE_TIME = 3.0

# PAYLOAD BUFFER
PALLET_BUFFER_PROCESS_TIME = 3.0
BATCH_BUFFER_PROCESS_TIME = 1.5

# DEPALLETIZER
DEPALLETIZING_DELAY = 1.0
ITEM_PROCESS_TIME = 1.0
ORDER_MERGE_TIME = 5.0

# BATCH BUILDER
BATCH_MAX_WAIT_TIME = 10.0


# -------------------------------
# Transportation unit constraints
# -------------------------------

MAX_ITEM_BATCH = 10

WAREHOUSE_MAX_PALLET_CAPACITY = 100

# -----------------
# Pallet properties
# -----------------

EURO_PALLET_MAX_WEIGHT = 1000.0    # kg
EURO_PALLET_MAX_VOLUME = 2112.0    # dm^3 (Area x Height = 0.8m x 1.2m x 2.2m)