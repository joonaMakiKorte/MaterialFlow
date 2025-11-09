# Factory Material Flow Simulator

A discrete-event **factory automation simulator and SCADA-like system** built with **SimPy** and **PyQt6**.  
It models warehouse logistics such as pallet movement, stock management, and order handling — while providing a real-time graphical interface similar to a **supervisory control and data acquisition (SCADA)** environment.

---

## Overview

The Factory Simulator combines a **SimPy-based simulation engine** with a **PyQt6-powered visualization layer**.  
It behaves like a simplified SCADA system where users can monitor, control, and analyze material flow inside a virtual warehouse or production environment.

The simulator manages:
- Payload transportation through components
- Material flow management
- Dynamic order placement and processing  
- Real-time GUI visualization of system activity  
- Event-based communication between simulation logic and interface

---

## Architecture

```plaintext
│
├── data/                            # Contains static data files, e.g., items.json for seeding the DB.
├── docs/                            # System documentation.
├── simulator/                       # Main application source code.
│   ├── core/                        # The core simulation logic.
│   │   ├── components/              # The main components representing the physical factory layout.
│   │   ├── factory/                 # The orchestration layer.
│   │   ├── items/                   # Item master data.
│   │   ├── orders/                  # Order classes and interface for placing orders.
│   │   ├── stock/                   # Stock classes and inventory management logic.
│   │   ├── transportation_units/    # Transportation units for factory payloads. 
│   │   └── utils/                   # Core application-wide components (LogManager, EventBus).
│   ├── database/                    # Database-related code (models, DatabaseManager, DatabaseListener).
│   ├── simulation/                  # The core simulation logic (Factory, Pallet, Order classes).
│   ├── gui/                         # PyQt6 user interface components (MainWindow, scenes).
│   ├── application.py               # The composition root of the application.
│   └── config.py                    # Simulation-wide constants.
├── tests/                           # Pytest test suite.
├── app.py                           # Main application entry point.
└── README.md                        # This file.
```

## Roadmap

### v0.4 — Simulation Core DEMO (DONE)
- Core simulation & SCADA-style GUI
- Event bus communication layer
- Order-flow demo
  - Ordering from Warehouse to Material Flow system

### v0.5 - Full Simulation Core (DONE)
- Material Flow routing and automatic orders.
- Database integration.
- Factory log visualization.

### v0.6 — Advanced Visualization (IN PROGRESS)
- Add live speed controls.
- Add detailed payload tracking overlay.
- Real-time analytics dashboard.

### v1.0 — Full Material Flow Simulator (GOAL)
- Support multiple factory layouts.
- Enable data export and analysis.
- Error logging and handling. 
  
## Technologies Used

| Category | Technology |
|-----------|-------------|
| Simulation Engine | [SimPy](https://simpy.readthedocs.io/) |
| GUI / SCADA Frontend | [PyQt6](https://doc.qt.io/qtforpython/) |
| Language | Python 3.10+ |
| Database | SQLite (via `DatabaseManager`) |
| Event System | Custom Event Bus for GUI sync |
| Testing | [pytest](https://docs.pytest.org/en/stable/) |
