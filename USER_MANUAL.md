# Cylinder Management System - User Manual

## Introduction

The Cylinder Management System is a desktop application designed to help you track and manage gas cylinders, customers, and dispatch operations. It provides a user-friendly interface for managing inventory, customer information, and cylinder movements between customers and your warehouse.

### Key Features
- **Customer Management**: Add, edit, and search customer information
- **Inventory Management**: Track cylinder status, add new cylinders, and generate reports
- **Dispatch & Returns**: Manage cylinder dispatches to customers and returns to warehouse
- **Reporting**: Generate inventory reports and customer bills

## Getting Started

### System Requirements
- Windows, macOS, or Linux operating system
- Python 3.6 or higher (usually pre-installed)
- No additional software installation required

### Installation and Launch
1. Download or copy the application files to your computer
2. Extract the zip file.
3. Navigate to the application folder
4. Open the application 'Cylinder_Management_System'
5. The login screen will appear

### Logging In
1. Enter your username and password
2. Default credentials: `admin` / `admin123`
3. Click "Login" or press Enter

## Main Interface

After logging in, you'll see the main application window with:
- **Header**: Application title
- **Menu Bar**: File menu with Logout and Exit options
- **Navigation Tabs**: Three main sections
  - Customer Management
  - Inventory Management
  - Dispatch & Returns

## Customer Management

This section allows you to manage your customer database.

### Adding a Customer
1. Click the "Add Customer" button
2. Fill in the customer details:
   - Name (required)
   - Contact Info
   - Address
   - Notes
3. Click "Save"

### Editing a Customer
1. Select a customer from the list (single-click)
2. Click "Edit Customer" or double-click the customer row
3. Modify the information in the dialog
4. Click "Save"

### Deleting a Customer
1. Select a customer from the list
2. Click "Delete Customer"
3. Confirm the deletion

### Searching Customers
1. Type in the search box to filter customers by name, contact info, or other details
2. The list updates automatically as you type

## Inventory Management

This section manages your cylinder inventory.

### Cylinder Status Types
- **Available**: Ready for dispatch
- **Dispatched**: Currently with a customer
- **Returned**: Back from customer, needs processing
- **Refill**: Needs refilling
- **Maintenance**: Under maintenance

### Adding Cylinders
1. Click "Add Cylinder"
2. Enter cylinder details:
   - Cylinder ID(s): Enter multiple IDs separated by commas
   - Product: Select from dropdown (Oxygen, Nitrogen, etc.)
   - Status: Select initial status
   - Location: Enter storage location
3. Click "Save"

### Managing Cylinder Status
1. Use the status tabs (All, Available, Dispatched, etc.) to filter cylinders
2. Select cylinders using the checkboxes
3. For bulk status updates:
   - Select cylinders with "refill" or "returned" status
   - Click "Update Status"
   - Choose new status (available or refill)

### Editing Cylinders
1. Select a cylinder from the list
2. Click "Edit Cylinder"
3. Modify details (note: Cylinder ID cannot be changed)
4. Click "Save"

### Deleting Cylinders
- Only cylinders with "available" status can be deleted
- Select cylinders and click "Delete Cylinder"
- Confirm the deletion

### Generating Reports
1. Click "Generate Report"
2. View summary of cylinder counts by status and product type

## Dispatch & Returns

This section handles cylinder movements.

### Dispatching Cylinders

#### Method 1: From Operations Tab
1. Select a customer from the dropdown
2. Enter dispatch date (DD-MM-YYYY format)
3. Enter or auto-generate DC Number
4. Enter Grade (required)
5. Select cylinders from the "Available Cylinders" list
6. Or enter cylinder IDs manually in the text field
7. Click "Dispatch Selected"

#### Method 2: From Available Cylinders Tab
1. Switch to "Available Cylinders" tab
2. Filter cylinders as needed
3. Select cylinders using checkboxes
4. Click "Return Selected Cylinders" (this dispatches them)

### Returning Cylinders

#### Method 1: From Operations Tab
1. Select DC Number from dropdown
2. Select cylinders to return from the list
3. Enter return date
4. Click "Return Selected"

#### Method 2: From History View
1. In the Operations tab, right panel shows dispatch history
2. Filter by status, company, or DC as needed
3. Select cylinders using checkboxes
4. Click "Return Selected"

#### Method 3: From Available Cylinders Tab
1. Switch to "Available Cylinders" tab
2. Filter to show dispatched cylinders
3. Select cylinders using checkboxes
4. Click "Return Selected Cylinders"

### Viewing History
- Use filters to find specific dispatches
- Double-click "Delete" column to remove returned records
- Export data to Excel or generate PDF bills

### Generating Bills
1. Select a specific DC or company from filters
2. Click "Generate Bill"
3. Choose save location for PDF
4. Optionally print the bill

## Troubleshooting

### Common Issues

**Cannot Login**
- Verify username and password
- Default: admin/admin123
- Check for caps lock


**Data Not Saving**
- Check database file permissions
- Ensure application has write access to folder

**Cylinder Status Not Updating**
- Only "refill" and "returned" cylinders can be updated
- Select cylinders before clicking "Update Status"

### Data Storage
- All data is stored locally in `cylinder_management.db`
- Backup this file regularly
- No internet connection required

## Support

For technical support or questions:
- Contact: 8888308567

---

*This manual covers the basic operation of the Cylinder Management System. For advanced features or custom configurations, please consult your system administrator.*