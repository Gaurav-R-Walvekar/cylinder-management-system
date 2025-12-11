#!/usr/bin/env python3
"""
Dispatch Tracking Frame for Cylinder Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import dispatch_cylinders, return_cylinders, get_all_dispatches, get_all_customers, get_cylinders_by_status, get_dispatched_cylinders_by_dc, generate_dc_number, get_connection
from models.dispatch import Dispatch
from models.customer import Customer

class DispatchTrackingFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.dispatches = []
        self.customers = []
        self.available_cylinders = []
        self.load_customers()
        self.load_available_cylinders()
        self.create_widgets()
        self.load_dispatches()

    def generate_dc_number(self):
        """Generate a unique DC number."""
        return generate_dc_number()

    def create_widgets(self):
        """Create dispatch tracking widgets."""
        # Title
        title_label = tk.Label(self, text="Dispatch & Return Tracking",
                              font=("Arial", 14, "bold"), fg='#2c3e50', bg='#f8f8f8')
        title_label.pack(pady=10)

        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel - Dispatch/Return operations
        left_panel = ttk.LabelFrame(main_frame, text="Operations", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Dispatch section
        dispatch_frame = tk.LabelFrame(left_panel, text="Dispatch Cylinders",
                                      font=("Arial", 10))
        dispatch_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(dispatch_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(dispatch_frame, textvariable=self.customer_var,
                                          values=[f"{c[0]} - {c[1]}" for c in self.customers],
                                          state="readonly", width=25)
        self.customer_combo.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(dispatch_frame, text="DC Number:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.dc_number_var = tk.StringVar()
        self.dc_number_entry = tk.Entry(dispatch_frame, textvariable=self.dc_number_var, width=27)
        # Generate initial DC number
        self.dc_number_var.set(self.generate_dc_number())
        self.dc_number_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(dispatch_frame, text="Available Cylinders:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        # Listbox for multiple cylinder selection
        self.cylinder_listbox = tk.Listbox(dispatch_frame, selectmode=tk.MULTIPLE, height=4, width=30)
        self.cylinder_listbox.grid(row=2, column=1, padx=5, pady=2)
        # Populate listbox
        for cylinder in self.available_cylinders:
            self.cylinder_listbox.insert(tk.END, f"{cylinder[0]} - {cylinder[1]} ({cylinder[2]})")

        tk.Label(dispatch_frame, text="Dispatch Date:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.dispatch_date_entry = tk.Entry(dispatch_frame, width=27)
        self.dispatch_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.dispatch_date_entry.grid(row=3, column=1, padx=5, pady=2)

        tk.Label(dispatch_frame, text="Notes:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.dispatch_notes_entry = tk.Text(dispatch_frame, width=20, height=3)
        self.dispatch_notes_entry.grid(row=4, column=1, padx=5, pady=2)

        tk.Button(dispatch_frame, text="Dispatch Selected", command=self.dispatch_cylinders).grid(row=5, column=0, columnspan=2, pady=10)

        # Return section
        return_frame = tk.LabelFrame(left_panel, text="Return Cylinders", font=("Arial", 10))
        return_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(return_frame, text="DC Number:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.dc_var = tk.StringVar()
        self.dc_combo = ttk.Combobox(return_frame, textvariable=self.dc_var,
                                    values=[], state="readonly", width=25)
        self.dc_combo.grid(row=0, column=1, padx=5, pady=2)
        self.dc_combo.bind('<<ComboboxSelected>>', self.on_dc_select)

        tk.Label(return_frame, text="Dispatched Cylinders:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.return_cylinder_listbox = tk.Listbox(return_frame, selectmode=tk.MULTIPLE, height=4, width=30)
        self.return_cylinder_listbox.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(return_frame, text="Return Date:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.return_date_entry = tk.Entry(return_frame, width=27)
        self.return_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.return_date_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(return_frame, text="Return Notes:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.return_notes_entry = tk.Text(return_frame, width=20, height=3)
        self.return_notes_entry.grid(row=3, column=1, padx=5, pady=2)

        tk.Button(return_frame, text="Return Selected", command=self.return_cylinders).grid(row=4, column=0, columnspan=2, pady=10)

        # Right panel - History view
        right_panel = tk.LabelFrame(main_frame, text="Dispatch History", font=("Arial", 10))
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Filter controls
        filter_frame = tk.Frame(right_panel)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filter_frame, text="Filter by Status:").pack(side=tk.LEFT, padx=5)

        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["All", "dispatched", "returned", "refill", "maintenance"],
                                   state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Button(filter_frame, text="Refresh", command=self.load_dispatches).pack(side=tk.RIGHT, padx=5)

        # Treeview for dispatches
        columns = ('ID', 'DC Number', 'Customer', 'Cylinder ID', 'Cylinder Type', 'Dispatch Date', 'Return Date', 'Status')
        self.tree = ttk.Treeview(right_panel, columns=columns, show='headings', height=18)

        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))

        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50, anchor='center')
            elif col == 'DC Number':
                self.tree.column(col, width=80)
            elif col == 'Cylinder Type':
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(right_panel, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_customers(self):
        """Load customers for dispatch combo."""
        self.customers = get_all_customers()
        # Update combo box if it exists
        if hasattr(self, 'customer_combo'):
            self.customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in self.customers]

    def load_available_cylinders(self):
        """Load available cylinders for dispatch listbox."""
        self.available_cylinders = get_cylinders_by_status('available')
        # Update the listbox display
        if hasattr(self, 'cylinder_listbox'):
            self.cylinder_listbox.delete(0, tk.END)
            for cylinder in self.available_cylinders:
                self.cylinder_listbox.insert(tk.END, f"{cylinder[0]} - {cylinder[1]} ({cylinder[2]})")

    def load_dispatches(self):
        """Load dispatches from database."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.dispatches = get_all_dispatches()
        for dispatch_row in self.dispatches:
            dispatch = Dispatch.from_db_row(dispatch_row)
            values = (dispatch.id, dispatch.dc_number, dispatch.customer_name, dispatch.cylinder_id_text,
                     dispatch.cylinder_type, dispatch.dispatch_date, dispatch.return_date, dispatch.status)
            self.tree.insert('', tk.END, values=values)

        # Update DC combo with unique DC numbers that have dispatched cylinders
        dc_numbers = list(set(d[1] for d in self.dispatches if d[8] == 'dispatched'))
        dc_numbers.sort(reverse=True)
        self.dc_combo['values'] = dc_numbers

    def on_filter_change(self, event=None):
        """Handle filter change."""
        filter_status = self.filter_var.get()
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if filter_status == "All":
            dispatches = self.dispatches
        else:
            dispatches = [d for d in self.dispatches if d[8] == filter_status]

        for dispatch_row in dispatches:
            dispatch = Dispatch.from_db_row(dispatch_row)
            values = (dispatch.id, dispatch.dc_number, dispatch.customer_name, dispatch.cylinder_id_text,
                     dispatch.cylinder_type, dispatch.dispatch_date, dispatch.return_date, dispatch.status)
            self.tree.insert('', tk.END, values=values)

    def on_dc_select(self, event=None):
        """Handle DC number selection for return."""
        dc_number = self.dc_var.get()
        if dc_number:
            # Load cylinders for this DC number
            self.return_cylinder_listbox.delete(0, tk.END)
            dispatched_cylinders = get_dispatched_cylinders_by_dc(dc_number)
            for cylinder in dispatched_cylinders:
                # Get cylinder type from database
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT cylinder_type FROM cylinders WHERE id = ?", (cylinder[0],))
                cylinder_type = cursor.fetchone()[0]
                conn.close()
                self.return_cylinder_listbox.insert(tk.END, f"{cylinder[0]} - {cylinder[1]} ({cylinder_type})")

    def dispatch_cylinders(self):
        """Dispatch selected cylinders to a customer."""
        customer_selection = self.customer_var.get()
        selected_indices = self.cylinder_listbox.curselection()
        dispatch_date = self.dispatch_date_entry.get().strip()
        dispatch_notes = self.dispatch_notes_entry.get("1.0", tk.END).strip()

        if not customer_selection:
            messagebox.showerror("Error", "Please select a customer.")
            return

        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one cylinder to dispatch.")
            return

        if not dispatch_date:
            messagebox.showerror("Error", "Please enter dispatch date.")
            return

        try:
            # Extract customer ID
            customer_id = int(customer_selection.split(' - ')[0])

            # Extract cylinder IDs
            cylinder_ids = []
            for index in selected_indices:
                cylinder_text = self.cylinder_listbox.get(index)
                cylinder_id = int(cylinder_text.split(' - ')[0])
                cylinder_ids.append(cylinder_id)

            dc_number = self.dc_number_var.get().strip()
            if not dc_number:
                dc_number = None  # Will generate new one
            dc_number = dispatch_cylinders(customer_id, cylinder_ids, dispatch_date, dispatch_notes, dc_number)
            self.load_dispatches()
            self.load_available_cylinders()

            self.customer_var.set('')
            self.dc_number_var.set(self.generate_dc_number())  # Generate new DC number for next dispatch
            self.dispatch_notes_entry.delete("1.0", tk.END)
            messagebox.showinfo("Success", f"Cylinders dispatched successfully under DC {dc_number}.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to dispatch cylinders: {e}")

    def return_cylinders(self):
        """Return selected cylinders."""
        dc_number = self.dc_var.get()
        selected_indices = self.return_cylinder_listbox.curselection()
        return_date = self.return_date_entry.get().strip()
        return_notes = self.return_notes_entry.get("1.0", tk.END).strip()

        if not dc_number:
            messagebox.showerror("Error", "Please select a DC number.")
            return

        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one cylinder to return.")
            return

        if not return_date:
            messagebox.showerror("Error", "Please enter return date.")
            return

        try:
            # Extract cylinder IDs
            cylinder_ids = []
            for index in selected_indices:
                cylinder_text = self.return_cylinder_listbox.get(index)
                cylinder_id = int(cylinder_text.split(' - ')[0])
                cylinder_ids.append(cylinder_id)

            return_cylinders(dc_number, cylinder_ids, return_date, return_notes)
            self.load_dispatches()
            self.load_available_cylinders()

            # Refresh return section
            self.dc_var.set('')
            self.return_cylinder_listbox.delete(0, tk.END)
            self.return_notes_entry.delete("1.0", tk.END)
            messagebox.showinfo("Success", "Cylinders returned successfully.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return cylinders: {e}")