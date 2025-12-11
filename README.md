# Cylinder Management System

A desktop application for tracking cylinders, customers, and dispatches built with Python and Tkinter.

## Features

### Login System
- Clean, professional login interface
- Secure authentication with username and password
- Default admin credentials: `admin` / `admin123`

### Customer Management
- Add, edit, delete, and view customer details
- Real-time search and filtering
- Professional table interface with double-click editing
- Fields: Name, Contact Info, Address, Notes

### Inventory Management
- Add new cylinders with ID, type, status, and location
- Update cylinder status (available, dispatched, returned, refill, maintenance)
- Advanced search and status filtering
- Generate inventory reports
- Admin can manage cylinder lifecycle

### Dispatch & Return Tracking
- **DC Numbers**: Unique Dispatch Control numbers for tracking (editable during dispatch)
- Dispatch multiple cylinders under single DC number
- Track returns by DC number with automatic refill workflow
- **Cylinder Types**: Displayed throughout the interface
- Professional dual-panel layout (Operations + History)
- Real-time data refresh when switching tabs
- Complete audit trail with filtering options

## Requirements

- Python 3.6+
- Tkinter (usually included with Python)
- SQLite3 (usually included with Python)

## Installation

1. Clone or download the project files
2. Ensure Python 3.6+ is installed
3. Run the application:

```bash
python main.py
```

## Usage

1. **Login**: Use default credentials `admin` / `admin123`
2. **Customer Management**: Add customers and manage their information
3. **Inventory Management**: Add cylinders and track their status
4. **Dispatch Tracking**: Dispatch cylinders to customers and track returns

## Project Structure

```
cylinder-management-system/
├── main.py                 # Application entry point
├── database.py            # SQLite database operations
├── gui/                   # GUI components
│   ├── __init__.py
│   ├── login.py           # Login screen
│   ├── main_window.py     # Main application window with tabs
│   ├── customer_management.py  # Customer management interface
│   ├── inventory_management.py # Inventory management interface
│   └── dispatch_tracking.py    # Dispatch and return tracking
└── models/                # Data models
    ├── __init__.py
    ├── customer.py        # Customer model
    ├── cylinder.py        # Cylinder model
    └── dispatch.py        # Dispatch model
```

## Database Schema

The application uses SQLite with the following tables:
- `customers`: Customer information
- `cylinders`: Cylinder inventory
- `dispatches`: Dispatch and return records
- `users`: User authentication

## Notes

- Data is stored locally in `cylinder_management.db`
- No external dependencies required beyond standard Python libraries
- Application runs on Windows, macOS, and Linux
