"""Simulation-wide constants"""

# -----------------
# Pallet properties
# -----------------

EURO_PALLET_MAX_WEIGHT = 1000.0    # kg
EURO_PALLET_MAX_VOLUME = 2112.0    # dm^3 (Area x Height = 0.8m x 1.2m x 2.2m)

# ---------------------------------------------------
# Operation times for elements in simulation units
# Simulation time unit = 1 second in simulation world
# ---------------------------------------------------

TIME_SCALE = 0.3 # seconds per simulation unit

CONVEYOR_CYCLE_TIME = 3.0
BUFFER_PROCESS_TIME = 3.0
ITEM_PROCESS_TIME = 2.0
ORDER_MERGE_TIME = 5.0


# -------------------------------
# Transportation unit constraints
# -------------------------------
MAX_ITEM_BATCH = 10