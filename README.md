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

The project follows a **modular architecture**:
- **`docs/`** # Full system documentation
- **`data/`** # Item definitions and layout for the factory
- **`simulator/`**
  - **`core/`** # Simulation logic (SimPy processes, orders, stock, conveyors)
  - **`gui/`** # PyQt6 GUI components, scene rendering, event handling
  - **`database/`**
  - **`config/`** # Global parameters and constants
- **`app.py`** # Entry point for running the simulator
- **`tests.py`** # Essential test files using pytest

## Technologies Used

| Category | Technology |
|-----------|-------------|
| Simulation Engine | [SimPy](https://simpy.readthedocs.io/) |
| GUI / SCADA Frontend | [PyQt6](https://doc.qt.io/qtforpython/) |
| Language | Python 3.10+ |
| Database | SQLite (via `DatabaseManager`) |
| Event System | Custom Event Bus for GUI sync |
