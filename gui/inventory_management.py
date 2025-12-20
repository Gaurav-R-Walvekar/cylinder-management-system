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

        tk.Label(search_frame, text="Filter by Status:", font=("Arial", 9),
                bg='#f8f9fa', fg='#2c3e50').pack(side=tk.LEFT, padx=10, pady=5)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_var,
                                   values=["All"] + self.status_options, state="readonly", width=15)
        status_combo.pack(side=tk.LEFT, padx=5, pady=5)
        status_combo.bind('<<ComboboxSelected>>', self.on_filter_status)

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

        # Custom table with radio buttons
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas for scrolling
        self.canvas = tk.Canvas(self.table_frame, bg='#f8f8f8')
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Header
        self.create_table_header()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_table_header(self):
        """Create table header."""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=2)

        ttk.Label(header_frame, text="Select", width=8, font=("Arial", 9, "bold")).grid(row=0, column=0, padx=2)
        ttk.Label(header_frame, text="ID", width=5, font=("Arial", 9, "bold")).grid(row=0, column=1, padx=2)
        ttk.Label(header_frame, text="Cylinder ID", width=15, font=("Arial", 9, "bold")).grid(row=0, column=2, padx=2)
        ttk.Label(header_frame, text="Type", width=15, font=("Arial", 9, "bold")).grid(row=0, column=3, padx=2)
        ttk.Label(header_frame, text="Status", width=20, font=("Arial", 9, "bold")).grid(row=0, column=4, padx=2)
        ttk.Label(header_frame, text="Location", width=15, font=("Arial", 9, "bold")).grid(row=0, column=5, padx=2)

    def create_table_row(self, cylinder, row_num):
        """Create a table row with checkbox and radio buttons for status."""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill=tk.X, pady=1)

        # Checkbox for selection
        check_var = tk.BooleanVar(value=False)
        self.check_vars[cylinder.id] = check_var
        cb = tk.Checkbutton(row_frame, variable=check_var)
        cb.grid(row=0, column=0, padx=2)

        # ID
        ttk.Label(row_frame, text=str(cylinder.id), width=5).grid(row=0, column=1, padx=2)

        # Cylinder ID
        ttk.Label(row_frame, text=cylinder.cylinder_id, width=15).grid(row=0, column=2, padx=2)

        # Type
        ttk.Label(row_frame, text=cylinder.cylinder_type, width=15).grid(row=0, column=3, padx=2)

        # Status as text
        ttk.Label(row_frame, text=cylinder.status.capitalize(), width=15).grid(row=0, column=4, padx=2)

        # Location
        ttk.Label(row_frame, text=cylinder.location or '', width=15).grid(row=0, column=5, padx=2)


    def refresh_table(self):
        """Refresh the table display."""
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.scrollable_frame.winfo_children()[0]:  # Keep header
                widget.destroy()

        self.check_vars = {}
        for i, cylinder_row in enumerate(self.cylinders, 1):
            cylinder = Cylinder.from_db_row(cylinder_row)
            self.create_table_row(cylinder, i)

    def load_cylinders(self):
        """Load cylinders from database."""
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.scrollable_frame.winfo_children()[0]:  # Keep header
                widget.destroy()

        self.cylinders = get_all_cylinders()
        self.check_vars = {}  # Store checkbox variables

        for i, cylinder_row in enumerate(self.cylinders, 1):
            cylinder = Cylinder.from_db_row(cylinder_row)
            self.create_table_row(cylinder, i)

    def on_search(self, event=None):
        """Handle search functionality."""
        query = self.search_var.get().strip()
        if query:
            self.cylinders = search_cylinders(query)
        else:
            self.cylinders = get_all_cylinders()
        self.refresh_table()

    def on_filter_status(self, event=None):
        """Handle status filtering."""
        status = self.status_var.get()
        if status == "All":
            self.cylinders = get_all_cylinders()
        else:
            self.cylinders = get_cylinders_by_status(status)
        self.refresh_table()

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
        """Update status of selected cylinders (bulk)."""
        selected_ids = [cid for cid, var in self.check_vars.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning("Warning", "Please select cylinders to update status.")
            return

        # Status selection dialog
        status_dialog = tk.Toplevel(self)
        status_dialog.title("Update Cylinder Status")
        status_dialog.geometry("300x150")
        status_dialog.resizable(False, False)
        status_dialog.transient(self)
        status_dialog.grab_set()

        ttk.Label(status_dialog, text=f"Update status for {len(selected_ids)} cylinders:").pack(pady=10)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_dialog, textvariable=status_var,
                                    values=self.status_options, state="readonly")
        status_combo.pack(pady=5)

        def save_status():
            new_status = status_var.get()
            if not new_status:
                messagebox.showerror("Error", "Please select a status.")
                return

            try:
                updated_count = 0
                for cid in selected_ids:
                    # Find cylinder data
                    for row in self.cylinders:
                        if row[0] == cid:
                            cylinder = Cylinder.from_db_row(row)
                            update_cylinder(cid, cylinder.cylinder_type, new_status, cylinder.location)
                            updated_count += 1
                            break
                self.load_cylinders()
                messagebox.showinfo("Success", f"Status updated for {updated_count} cylinders.")
                status_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {e}")

        ttk.Button(status_dialog, text="Update", command=save_status).pack(pady=10)

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

        # Create report dialog
        report_dialog = tk.Toplevel(self)
        report_dialog.title("Inventory Report")
        report_dialog.geometry("400x300")
        report_dialog.resizable(False, False)

        ttk.Label(report_dialog, text="Cylinder Inventory Report", font=("Arial", 14, "bold")).pack(pady=10)

        report_text = tk.Text(report_dialog, wrap=tk.WORD, height=15)
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        report_content = f"Total Cylinders: {total_cylinders}\n\n"
        for status, count in status_counts.items():
            report_content += f"{status.capitalize()}: {count}\n"

        report_text.insert(tk.END, report_content)
        report_text.config(state=tk.DISABLED)

        ttk.Button(report_dialog, text="Close", command=report_dialog.destroy).pack(pady=10)

class CylinderDialog:
    """Dialog for adding/editing cylinders."""
    def __init__(self, parent, title, cylinder=None):
        self.result = None
        self.status_options = ['available', 'dispatched', 'returned', 'refill', 'maintenance']
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

        ttk.Label(self.dialog, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.type_entry = ttk.Entry(self.dialog, width=30)
        self.type_entry.grid(row=1, column=1, padx=10, pady=5)

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
            self.type_entry.insert(0, cylinder.cylinder_type)
            self.status_var.set(cylinder.status)
            self.location_entry.insert(0, cylinder.location)

    def save(self):
        """Save cylinder data."""
        cylinder_id = self.cylinder_id_entry.get().strip()
        cylinder_type = self.type_entry.get().strip()
        status = self.status_var.get()
        location = self.location_entry.get().strip()

        if not status:
            status = 'available'  # Default status

        self.result = (cylinder_id, cylinder_type, status, location)
        self.dialog.destroy()

    def cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()