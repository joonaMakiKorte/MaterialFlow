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

# CONVEYOR
CONVEYOR_CYCLE_TIME = 3.0

# PAYLOAD BUFFER
PALLET_BUFFER_PROCESS_TIME = 3.0
BATCH_BUFFER_PROCESS_TIME = 2

# DEPALLETIZER
DEPALLETIZING_DELAY = 1.0
ITEM_PROCESS_TIME = 1.0

# BATCH BUILDER
BATCH_MAX_WAIT_TIME = 10.0

# STOCK ELEMENTS
ORDER_MERGE_TIME = 5.0
REQUESTED_ITEM_SCAN_INTERVAL = 20.0

# -------------------------------
# Transportation unit constraints
# -------------------------------

MAX_ITEM_BATCH = 10


# -----------------
# Stock constraints
# -----------------

WAREHOUSE_MAX_PALLET_CAPACITY = 25
ITEM_WAREHOUSE_MAX_ITEM_CAPACITY = 500

# -----------------
# Pallet properties
# -----------------

EURO_PALLET_MAX_WEIGHT = 1000.0    # kg
EURO_PALLET_MAX_VOLUME = 2112.0    # dm^3 (Area x Height = 0.8m x 1.2m x 2.2m)


# ------------------
# Logging properties
# ------------------

MAX_COMPONENT_LOG_COUNT = 50
