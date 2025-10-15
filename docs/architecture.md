# System Architecture

```mermaid
flowchart LR
    subgraph SimulationCore["Simulation Core (SimPy)"]
        subgraph Factory[Factory]
            Stock[Stock]
            Orders[Inventory Manager]
            Catalogue[Catalogue]
            Component[Components]
            Payloads[Transportation Units]
        end
    end

    subgraph GUI["GUI Layer (PyQt)"]
        View[Main Window]
        Scene[Factory Scene]
        Items[Gui Items]
    end

    subgraph DB["Database Layer (sqlite)"]
    end

    Config[Configuration] --> SimulationCore
    Data["Data (.json)"] --> SimulationCore
    SimulationCore -->|Event Bus| GUI
    GUI -->|User Interactions| SimulationCore
    SimulationCore -->|Database Manager| DB
    DB --> SimulationCore
