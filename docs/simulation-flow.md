
# Simulation Flow

### Payload Movement

Each component registers a Simpy process. When a process is completed, component emits an event through Event Bus for GUI updating.
Sequence example for moving a pallet through conveyors:

```mermaid
sequenceDiagram
    participant PayloadConveyor1
    participant PayloadConveyor2
    participant EventBus
    participant GUI

    PayloadConveyor1->>PayloadConveyor2: Check if can load
    PayloadConveyor2-->>PayloadConveyor1: Ready to load
    PayloadConveyor1->>PayloadConveyor2: Start loading process
    Note over PayloadConveyor1,PayloadConveyor2: Wait for CONVEYOR_CYCLE_TIME
    PayloadConveyor2->>EventBus: Emit 'move_pallet' event
    EventBus->>GUI: Update pallet position on screen
```

### Placing orders in GUI

The user may place manual orders through an order dialog. An Order-object is created in InventoryManager, placed in order queue in the stock requested, and stored in database.
Sequence example for placing an order:

```mermaid
sequenceDiagram
    participant GUI
    participant InventoryManager
    participant Catalogue
    participant Stock
    participant DatabaseManager

    GUI->>InventoryManager: Place manual order
    InventoryManager->>Catalogue: Get item details
    Catalogue-->>InventoryManager: Item info
    InventoryManager->>Stock: Add to order queue
    InventoryManager->>DatabaseManager: Save order record


```
  
