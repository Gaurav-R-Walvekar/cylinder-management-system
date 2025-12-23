#!/usr/bin/env python3
"""
Inventory Management Frame for Cylinder Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import add_cylinder, get_all_cylinders, update_cylinder, delete_cylinder, search_cylinders, get_cylinders_by_status
from models.cylinder import Cylinder

class InventoryManagementFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cylinders = []
        self.status_options = ['available', 'dispatched', 'returned', 'refill', 'maintenance']
        self.check_vars = {}
        self.selected_items = set()  # For tracking selected cylinder IDs
        self.status_notebook = None
        self.create_widgets()
        self.load_cylinders()

    def create_widgets(self):
        """Create inventory management widgets."""
        # Title
        title_label = tk.Label(self, text="Inventory Management",
                              font=("Arial", 14, "bold"), fg='#2c3e50', bg='#f8f8f8')
        title_label.pack(pady=10)

        # Search and filter frame
        search_frame = tk.LabelFrame(self, text="Search & Filter",
                                    font=("Arial", 10, "bold"), bg='#f8f9fa',
                                    fg='#2c3e50', relief='solid', bd=1)
        search_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(search_frame, text="Search Cylinders:", font=("Arial", 9),
                bg='#f8f9fa', fg='#2c3e50').pack(side=tk.LEFT, padx=10, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=25,
                                    font=("Arial", 9), relief='solid', bd=1)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)

        # Status filter removed, replaced with tabs

        # Buttons frame
        buttons_frame = tk.Frame(self, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(buttons_frame, text="Add Cylinder", font=("Arial", 9, "bold"),
                 bg='#4CAF50', fg='white', relief='raised', bd=1, padx=10, pady=3,
                 command=self.add_cylinder).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Edit Cylinder", font=("Arial", 9, "bold"),
                 bg='#FF9800', fg='white', relief='raised', bd=1, padx=10, pady=3,
                 command=self.edit_cylinder).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Delete Cylinder", font=("Arial", 9, "bold"),
                 bg='#F44336', fg='white', relief='raised', bd=1, padx=10, pady=3,
                 command=self.delete_cylinder).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Update Status", font=("Arial", 9, "bold"),
                 bg='#9C27B0', fg='white', relief='raised', bd=1, padx=10, pady=3,
                 command=self.update_status).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Generate Report", font=("Arial", 9, "bold"),
                 bg='#009688', fg='white', relief='raised', bd=1, padx=10, pady=3,
                 command=self.generate_report).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Refresh", font=("Arial", 9, "bold"),
                  bg='#2196F3', fg='white', relief='raised', bd=1, padx=10, pady=3,
                  command=self.load_cylinders).pack(side=tk.LEFT, padx=5)

        # Status tabs
        self.status_notebook = ttk.Notebook(self)
        self.status_notebook.pack(fill=tk.X, padx=15, pady=5)
        for status in ["All"] + self.status_options:
            tab_frame = ttk.Frame(self.status_notebook)
            self.status_notebook.add(tab_frame, text=status)
        self.status_notebook.select(0)  # Select All
        self.status_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Treeview for cylinders table
        columns = ('Select', 'ID', 'Cylinder ID', 'Product', 'Status', 'Location')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        
        # Configure colors for selected rows
        style.map('Treeview', background=[('selected', '#bbdefb')])
        
        # Configure tag for selection column
        self.tree.tag_configure('selected', foreground='#1976D2', font=('Arial', 12, 'bold'))
        self.tree.tag_configure('unselected', foreground="#000000", font=('Arial', 12))
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Select':
                self.tree.column(col, width=60, anchor='center')
            elif col == 'ID':
                self.tree.column(col, width=50, anchor='center')
            elif col == 'Cylinder ID':
                self.tree.column(col, width=120)
            elif col == 'Product':
                self.tree.column(col, width=120)
            elif col == 'Status':
                self.tree.column(col, width=100)
            elif col == 'Location':
                self.tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15))
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=15)
        
        # Bind click event for selection toggle
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # Select All checkbox frame
        select_frame = tk.Frame(self, bg='#f8f8f8')
        select_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        self.select_all_var = tk.BooleanVar()
        select_all_cb = tk.Checkbutton(select_frame, text="Select All", variable=self.select_all_var, 
                                       command=self.toggle_select_all, bg='#f8f8f8', fg='#2c3e50',
                                       activebackground='#e3f2fd', activeforeground='#1976D2',
                                       selectcolor='#bbdefb', font=('Arial', 9, 'bold'))
        select_all_cb.pack(side=tk.LEFT, padx=5)

    def on_tree_click(self, event):
        """Handle click on treeview for select toggle."""
        region = self.tree.identify_region(event.x, event.y)
        if region == 'cell':
            item = self.tree.identify_row(event.y)
            if item:
                cylinder_id = self.tree.item(item, 'values')[1]  # ID is in column 2
                if cylinder_id in self.selected_items:
                    self.selected_items.remove(cylinder_id)
                    self.tree.item(item, tags=('unselected',))
                else:
                    self.selected_items.add(cylinder_id)
                    self.tree.item(item, tags=('selected',))
                # Update display
                select_text = '✓' if cylinder_id in self.selected_items else ''
                self.tree.set(item, 'Select', select_text)
                    
    def toggle_select_all(self):
        """Toggle select all checkboxes."""
        state = self.select_all_var.get()
        if state:
            # Select all
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                cylinder_id = values[1]
                self.selected_items.add(cylinder_id)
                self.tree.set(item, 'Select', '✓')
                self.tree.item(item, tags=('selected',))
        else:
            # Deselect all
            self.selected_items.clear()
            for item in self.tree.get_children():
                self.tree.set(item, 'Select', '')
                self.tree.item(item, tags=('unselected',))

    def load_cylinders(self):
        """Load cylinders from database."""
        # Clear selection
        self.selected_items.clear()
        self.select_all_var.set(False)
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cylinders = get_all_cylinders()
        
        for cylinder_row in self.cylinders:
            cylinder = Cylinder.from_db_row(cylinder_row)
            is_selected = cylinder.id in self.selected_items
            select_text = '✓' if is_selected else ''
            tags = ('selected',) if is_selected else ('unselected',)
            self.tree.insert('', tk.END, values=(
                select_text,
                cylinder.id,
                cylinder.cylinder_id,
                cylinder.cylinder_type,
                cylinder.status.capitalize(),
                cylinder.location or ''
            ), tags=tags)

    def on_search(self, event=None):
        """Handle search functionality."""
        query = self.search_var.get().strip()
        if query:
            all_cylinders = search_cylinders(query)
        else:
            all_cylinders = get_all_cylinders()
        current_status = self.get_current_status()
        if current_status == "All":
            self.cylinders = all_cylinders
        else:
            self.cylinders = [c for c in all_cylinders if Cylinder.from_db_row(c).status == current_status.lower()]
        self.refresh_table()

    def on_filter_status(self, status):
        """Handle status filtering."""
        query = self.search_var.get().strip()
        if query:
            all_cylinders = search_cylinders(query)
        else:
            all_cylinders = get_all_cylinders()
        if status == "All":
            self.cylinders = all_cylinders
        else:
            self.cylinders = [c for c in all_cylinders if Cylinder.from_db_row(c).status == status.lower()]
        self.refresh_table()

    def refresh_table(self):
        """Refresh the table display."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for cylinder_row in self.cylinders:
            cylinder = Cylinder.from_db_row(cylinder_row)
            is_selected = cylinder.id in self.selected_items
            select_text = '✓' if is_selected else ''
            tags = ('selected',) if is_selected else ('unselected',)
            self.tree.insert('', tk.END, values=(
                select_text,
                cylinder.id,
                cylinder.cylinder_id,
                cylinder.cylinder_type,
                cylinder.status.capitalize(),
                cylinder.location or ''
            ), tags=tags)

    def get_current_status(self):
        """Get the currently selected status tab."""
        current_tab = self.status_notebook.index(self.status_notebook.select())
        return self.status_notebook.tab(current_tab, "text")

    def on_tab_changed(self, event):
        """Handle tab change to filter by status."""
        status = self.get_current_status()
        self.on_filter_status(status)

    def add_cylinder(self):
        """Add new cylinder dialog."""
        dialog = CylinderDialog(self, "Add Cylinder")
        if dialog.result:
            try:
                cylinder_id, cylinder_type, status, location = dialog.result
                if not cylinder_id.strip() or not cylinder_type.strip():
                    messagebox.showerror("Error", "Cylinder ID and Type are required.")
                    return
                add_cylinder(cylinder_id, cylinder_type, status, location)
                self.load_cylinders()
                messagebox.showinfo("Success", "Cylinder added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add cylinder: {e}")

    def edit_cylinder(self):
        """Edit selected cylinder."""
        cylinder_data = self.select_cylinder()
        if not cylinder_data:
            return

        dialog = CylinderDialog(self, "Edit Cylinder", cylinder_data)
        if dialog.result:
            try:
                cylinder_id, cylinder_type, status, location = dialog.result
                if not cylinder_id.strip() or not cylinder_type.strip():
                    messagebox.showerror("Error", "Cylinder ID and Type are required.")
                    return
                update_cylinder(cylinder_data.id, cylinder_type, status, location)
                self.load_cylinders()
                messagebox.showinfo("Success", "Cylinder updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update cylinder: {e}")

    def delete_cylinder(self):
        """Delete selected cylinder."""
        cylinder_data = self.select_cylinder()
        if not cylinder_data:
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete cylinder {cylinder_data.cylinder_id}?"):
            return

        try:
            delete_cylinder(cylinder_data.id)
            self.load_cylinders()
            messagebox.showinfo("Success", "Cylinder deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete cylinder: {e}")

    def update_status(self):
        """Update status of selected cylinders."""
        selected_ids = list(self.selected_items)
        if not selected_ids:
            messagebox.showwarning("Warning", "Please select cylinders to update status.")
            return

        # Get all cylinders from database to search through (not just filtered ones)
        all_cylinders = get_all_cylinders()
        
        # Filter to cylinders with 'refill' or 'returned' status
        valid_ids = []
        for cid in selected_ids:
            # Convert cid to int since treeview values are strings
            cid_int = int(cid)
            for row in all_cylinders:
                if row[0] == cid_int:
                    cylinder = Cylinder.from_db_row(row)
                    if cylinder.status in ['refill', 'returned', 'Refill', 'Returned']:
                        valid_ids.append(cid)
                    break

        if not valid_ids:
            messagebox.showerror("Error", "Only cylinders with 'refill' or 'returned' status can be updated.")
            return

        # Show status selection dialog
        dialog = StatusUpdateDialog(self, len(valid_ids))
        if not dialog.result:
            return

        new_status = dialog.result

        # Confirm update
        if not messagebox.askyesno("Confirm Update", f"Update status to '{new_status}' for {len(valid_ids)} selected cylinders?"):
            return

        try:
            updated_count = 0
            for cid in valid_ids:
                # Convert cid to int since treeview values are strings
                cid_int = int(cid)
                # Find cylinder data from all cylinders
                for row in all_cylinders:
                    if row[0] == cid_int:
                        cylinder = Cylinder.from_db_row(row)
                        update_cylinder(cid_int, cylinder.cylinder_type, new_status, cylinder.location)
                        updated_count += 1
                        break
            self.load_cylinders()
            messagebox.showinfo("Success", f"Status updated to '{new_status}' for {updated_count} cylinders.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {e}")

    def select_cylinder(self):
        """Select a cylinder from list."""
        if not self.cylinders:
            messagebox.showwarning("Warning", "No cylinders available.")
            return None

        select_dialog = tk.Toplevel(self)
        select_dialog.title("Select Cylinder")
        select_dialog.geometry("400x300")
        select_dialog.resizable(False, False)
        select_dialog.transient(self)
        select_dialog.grab_set()

        ttk.Label(select_dialog, text="Select a cylinder:").pack(pady=10)

        listbox = tk.Listbox(select_dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for row in self.cylinders:
            cylinder = Cylinder.from_db_row(row)
            listbox.insert(tk.END, f"{cylinder.id} - {cylinder.cylinder_id} ({cylinder.cylinder_type}) - {cylinder.status}")

        selected = [None]

        def on_select():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                row = self.cylinders[index]
                selected[0] = Cylinder.from_db_row(row)
                select_dialog.destroy()

        ttk.Button(select_dialog, text="Select", command=on_select).pack(pady=10)

        select_dialog.wait_window()
        return selected[0]

    def generate_report(self):
        """Generate basic inventory report."""
        # Count cylinders by status
        status_counts = {}
        for status in self.status_options:
            status_counts[status] = len(get_cylinders_by_status(status))

        total_cylinders = len(get_all_cylinders())

        # Count cylinders by product
        product_counts = {}
        for row in get_all_cylinders():
            cylinder = Cylinder.from_db_row(row)
            product = cylinder.cylinder_type
            product_counts[product] = product_counts.get(product, 0) + 1

        # Create report dialog
        report_dialog = tk.Toplevel(self)
        report_dialog.title("Inventory Report")
        report_dialog.geometry("400x400")  # Increased height for more content
        report_dialog.resizable(False, False)

        ttk.Label(report_dialog, text="Cylinder Inventory Report", font=("Arial", 14, "bold")).pack(pady=10)

        report_text = tk.Text(report_dialog, wrap=tk.WORD, height=20)  # Increased height
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        report_content = f"Total Cylinders: {total_cylinders}\n\n"
        report_content += "Status Counts:\n"
        for status, count in status_counts.items():
            report_content += f"{status.capitalize()}: {count}\n"

        report_content += f"\nProduct Counts:\n"
        for product, count in sorted(product_counts.items()):
            report_content += f"{product}: {count}\n"

        report_text.insert(tk.END, report_content)
        report_text.config(state=tk.DISABLED)

        ttk.Button(report_dialog, text="Close", command=report_dialog.destroy).pack(pady=10)

class CylinderDialog:
    """Dialog for adding/editing cylinders."""
    def __init__(self, parent, title, cylinder=None):
        self.result = None
        self.status_options = ['available', 'dispatched', 'returned', 'refill', 'maintenance']
        self.product_options = ['Oxygen', 'Nitrogen', 'Argon', 'Hydrogen', 'Carbon dioxide', 'Zero air', 'Helium', 'Dissolved Acetylene', 'Liquid nitrogen', 'Nitrous oxide', 'Mixtures', 'Medical Oxygen']
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets(cylinder)
        self.dialog.wait_window()

    def create_widgets(self, cylinder):
        """Create dialog widgets."""
        # Labels and entries
        ttk.Label(self.dialog, text="Cylinder ID:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.cylinder_id_entry = ttk.Entry(self.dialog, width=30)
        self.cylinder_id_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.dialog, text="Product:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(self.dialog, textvariable=self.product_var,
                                          values=self.product_options, state="readonly", width=27)
        self.product_combo.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.dialog, text="Status:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(self.dialog, textvariable=self.status_var,
                                        values=self.status_options, state="readonly", width=27)
        self.status_combo.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.dialog, text="Location:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.location_entry = ttk.Entry(self.dialog, width=30)
        self.location_entry.grid(row=3, column=1, padx=10, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=10)

        # Populate fields if editing
        if cylinder:
            self.cylinder_id_entry.insert(0, cylinder.cylinder_id)
            self.cylinder_id_entry.config(state="disabled")  # Don't allow editing cylinder ID
            self.product_var.set(cylinder.cylinder_type)
            self.status_var.set(cylinder.status)
            self.location_entry.insert(0, cylinder.location)

    def save(self):
        """Save cylinder data."""
        cylinder_id = self.cylinder_id_entry.get().strip()
        cylinder_type = self.product_var.get().strip()
        status = self.status_var.get()
        location = self.location_entry.get().strip()

        if not status:
            status = 'available'  # Default status

        self.result = (cylinder_id, cylinder_type, status, location)
        self.dialog.destroy()

    def cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()


class StatusUpdateDialog:
    """Dialog for selecting new status for cylinders."""
    def __init__(self, parent, cylinder_count):
        self.result = None
        self.status_options = ['refill', 'available']
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Cylinder Status")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets(cylinder_count)
        self.dialog.wait_window()

    def create_widgets(self, cylinder_count):
        """Create dialog widgets."""
        ttk.Label(self.dialog, text=f"Update status for {cylinder_count} cylinder(s):").pack(pady=10)

        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(self.dialog, textvariable=self.status_var,
                                        values=self.status_options, state="readonly", width=20)
        self.status_combo.pack(pady=5)
        self.status_combo.set('available')  # Default selection

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Update", command=self.update).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=10)

    def update(self):
        """Set the selected status."""
        status = self.status_var.get()
        if status:
            self.result = status
            self.dialog.destroy()

    def cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()