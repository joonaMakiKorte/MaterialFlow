
# Simulation Flow

### Payload Movement

Each component registers a Simpy process. When a process is completed, component emits an event through Event Bus for GUI updating.
Sequence example for moving a payload through conveyors:

```mermaid
sequenceDiagram
    participant PayloadConveyor1
    participant PayloadConveyor2
    participant LogManager
    participant EventBus
    participant GUI

    PayloadConveyor1->>PayloadConveyor2: Check if can load
    PayloadConveyor2-->>PayloadConveyor1: Ready to load

    PayloadConveyor1->>LogManager: log("Unloading payload {payload_id}", "PayloadConveyor1")
    PayloadConveyor1->>PayloadConveyor2: Start loading process
    
    Note over PayloadConveyor1,PayloadConveyor2: Wait for CONVEYOR_CYCLE_TIME

    PayloadConveyor2->>LogManager: log("Loaded payload {payload_id}", "PayloadConveyor2")
    PayloadConveyor2->>EventBus: Emit 'move_payload' event
    EventBus->>GUI: Update payload position on screen
```

### Placing orders in GUI

The user may place manual orders through an order dialog. An Order-object is created in InventoryManager, placed in order queue in the stock requested, and stored in database.
The stock requested may also place internal Refill orders if needed. Sequence example for placing an order:

```mermaid
sequenceDiagram
    participant GUI
    participant InventoryManager
    participant Catalogue
    participant Stock
    participant FactorySystem
    participant ProcurementSystem
    participant DatabaseManager

    %% --- Section 1: Placing a New Order ---
    GUI->>InventoryManager: Place manual order
    InventoryManager->>Catalogue: Get item details
    Catalogue-->>InventoryManager: Item info

    InventoryManager->>Stock: Add to order queue
    InventoryManager->>DatabaseManager: Save order record
    Note right of Stock: Order is now in the main queue, pending validation.

    %% --- Section 2: Stock's Internal Processing of the Order ---
    alt Stock has sufficient items
        Stock->>Stock: Validate order stock
        Stock->>FactorySystem: Dispatch processable order
        Note right of FactorySystem: Order moves to the 'processable' queue.

    else Stock has insufficient items
        Stock->>Stock: Validate order stock
        Stock->>Stock: Save item request to internal requested_items_queue
        Note over Stock: Order remains in a pending state. The shortage is now flagged internally.
    end

    %% --- Section 3: InventoryManager's Refill Management Loop ---
    loop Periodically Check for Stock Needs
        InventoryManager->>Stock: Get required items from queue
        Stock-->>InventoryManager: Aggregated list of needed items
        
        opt List is not empty
            InventoryManager->>ProcurementSystem: Generate and send refill order
            ProcurementSystem-->>InventoryManager: Refill order confirmed
        end
    end
```
  
