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

TIME_SCALE = 3.0

def scale_time(t):
    """Scales a base process time according to the global simulation speed."""
    return t / TIME_SCALE

# CONVEYOR
CONVEYOR_CYCLE_TIME = scale_time(3.0)

# PAYLOAD BUFFER
PALLET_BUFFER_PROCESS_TIME = scale_time(3.0)
BATCH_BUFFER_PROCESS_TIME = scale_time(2)

# DEPALLETIZER
DEPALLETIZING_DELAY = scale_time(1.0)
ITEM_PROCESS_TIME = scale_time(1.0)
ORDER_MERGE_TIME = scale_time(5.0)

# BATCH BUILDER
BATCH_MAX_WAIT_TIME = scale_time(10.0)


# -------------------------------
# Transportation unit constraints
# -------------------------------

MAX_ITEM_BATCH = 10

WAREHOUSE_MAX_PALLET_CAPACITY = 25


# -----------------
# Pallet properties
# -----------------

EURO_PALLET_MAX_WEIGHT = 1000.0    # kg
EURO_PALLET_MAX_VOLUME = 2112.0    # dm^3 (Area x Height = 0.8m x 1.2m x 2.2m)
