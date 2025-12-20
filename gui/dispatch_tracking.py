#!/usr/bin/env python3
"""
Dispatch Tracking Frame for Cylinder Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database import dispatch_cylinders, return_cylinders, get_all_dispatches, get_all_customers, get_cylinders_by_status, get_dispatched_cylinders_by_dc, generate_dc_number, get_connection
from models.dispatch import Dispatch
from models.customer import Customer
try:
    from openpyxl import Workbook
except ImportError:
    messagebox.showerror("Missing Library", "openpyxl is required for Excel export. Please install it with: pip install openpyxl")
    Workbook = None

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

        tk.Label(dispatch_frame, text="Available Cylinders:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        # Frame for listbox and scrollbar
        cylinder_frame = tk.Frame(dispatch_frame)
        cylinder_frame.grid(row=2, column=1, padx=5, pady=5)
        # Listbox for multiple cylinder selection
        self.cylinder_listbox = tk.Listbox(cylinder_frame, selectmode=tk.MULTIPLE, height=4, width=30)
        self.cylinder_listbox.pack(side=tk.LEFT)
        cylinder_scrollbar = tk.Scrollbar(cylinder_frame, orient=tk.VERTICAL, command=self.cylinder_listbox.yview)
        self.cylinder_listbox.config(yscrollcommand=cylinder_scrollbar.set)
        cylinder_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cylinder_listbox.bind('<<ListboxSelect>>', lambda e: self.update_selected_cylinders())
        # Populate listbox
        for cylinder in self.available_cylinders:
            self.cylinder_listbox.insert(tk.END, f"{cylinder[0]} - {cylinder[1]} ({cylinder[2]})")

        tk.Label(dispatch_frame, text="Manual Cylinder IDs:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.manual_cylinder_entry = tk.Entry(dispatch_frame, width=27)
        self.manual_cylinder_entry.grid(row=3, column=1, padx=5, pady=2)
        self.manual_cylinder_entry.bind('<Return>', lambda e: self.update_selected_cylinders())
        self.manual_cylinder_entry.bind('<FocusOut>', lambda e: self.update_selected_cylinders())
        tk.Label(dispatch_frame, text="(Comma-separated IDs)").grid(row=3, column=2, padx=5, pady=2, sticky="w")

        tk.Label(dispatch_frame, text="Selected Cylinders:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        # Frame for listbox and scrollbar
        selected_frame = tk.Frame(dispatch_frame)
        selected_frame.grid(row=4, column=1, padx=5, pady=5)
        self.selected_cylinders_listbox = tk.Listbox(selected_frame, height=3, width=30)
        self.selected_cylinders_listbox.pack(side=tk.LEFT)
        selected_scrollbar = tk.Scrollbar(selected_frame, orient=tk.VERTICAL, command=self.selected_cylinders_listbox.yview)
        self.selected_cylinders_listbox.config(yscrollcommand=selected_scrollbar.set)
        selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(dispatch_frame, text="Update Selected", command=self.update_selected_cylinders).grid(row=4, column=2, padx=5, pady=5)

        tk.Label(dispatch_frame, text="Dispatch Date:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.dispatch_date_entry = tk.Entry(dispatch_frame, width=27)
        self.dispatch_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.dispatch_date_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(dispatch_frame, text="Grade:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.grade_entry = tk.Entry(dispatch_frame, width=27)
        self.grade_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(dispatch_frame, text="Dispatch Selected", command=self.dispatch_cylinders).grid(row=7, column=0, columnspan=2, pady=10)

        # Return section
        return_frame = tk.LabelFrame(left_panel, text="Return Cylinders", font=("Arial", 10))
        return_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(return_frame, text="DC Number:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.dc_var = tk.StringVar()
        self.dc_combo = ttk.Combobox(return_frame, textvariable=self.dc_var,
                                    values=[], state="readonly", width=25)
        self.dc_combo.grid(row=0, column=1, padx=5, pady=2)
        self.dc_combo.bind('<<ComboboxSelected>>', self.on_dc_select)

        tk.Label(return_frame, text="Dispatched Cylinders:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        # Frame for listbox and scrollbar
        return_cylinder_frame = tk.Frame(return_frame)
        return_cylinder_frame.grid(row=1, column=1, padx=5, pady=5)
        self.return_cylinder_listbox = tk.Listbox(return_cylinder_frame, selectmode=tk.MULTIPLE, height=4, width=30)
        self.return_cylinder_listbox.pack(side=tk.LEFT)
        return_scrollbar = tk.Scrollbar(return_cylinder_frame, orient=tk.VERTICAL, command=self.return_cylinder_listbox.yview)
        self.return_cylinder_listbox.config(yscrollcommand=return_scrollbar.set)
        return_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(return_frame, text="Return Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.return_date_entry = tk.Entry(return_frame, width=27)
        self.return_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.return_date_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(return_frame, text="Return Selected", command=self.return_cylinders).grid(row=3, column=0, columnspan=2, pady=10)

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

        tk.Label(filter_frame, text="Filter by Company:").pack(side=tk.LEFT, padx=5)

        self.company_filter_var = tk.StringVar(value="All")
        self.company_filter_combo = ttk.Combobox(filter_frame, textvariable=self.company_filter_var,
                                                 values=["All"] + [f"{c[0]} - {c[1]}" for c in self.customers],
                                                 state="readonly", width=20)
        self.company_filter_combo.pack(side=tk.LEFT, padx=5)
        self.company_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Label(filter_frame, text="Filter by DC:").pack(side=tk.LEFT, padx=5)

        self.dc_filter_var = tk.StringVar(value="All")
        self.dc_filter_combo = ttk.Combobox(filter_frame, textvariable=self.dc_filter_var,
                                            values=["All"], state="readonly", width=15)
        self.dc_filter_combo.pack(side=tk.LEFT, padx=5)
        self.dc_filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        tk.Button(filter_frame, text="Generate Bill", command=self.generate_bill).pack(side=tk.RIGHT, padx=5)
        tk.Button(filter_frame, text="Export to Excel", command=self.export_to_excel).pack(side=tk.RIGHT, padx=5)
        tk.Button(filter_frame, text="Refresh", command=self.load_dispatches).pack(side=tk.RIGHT, padx=5)

        # Treeview for dispatches
        columns = ('ID', 'DC Number', 'Customer', 'Cylinder ID', 'Cylinder Type', 'Grade', 'Dispatch Date', 'Return Date', 'Status', 'Delete')
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
            elif col == 'Grade':
                self.tree.column(col, width=80)
            elif col == 'Delete':
                self.tree.column(col, width=60, anchor='center')
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

        # Bind double-click for delete
        self.tree.bind('<Double-1>', self.on_tree_double_click)

    def load_customers(self):
        """Load customers for dispatch combo."""
        self.customers = get_all_customers()
        # Update combo boxes if they exist
        if hasattr(self, 'customer_combo'):
            self.customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in self.customers]
        if hasattr(self, 'company_filter_combo'):
            self.company_filter_combo['values'] = ["All"] + [f"{c[0]} - {c[1]}" for c in self.customers]

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
            delete_text = 'Delete' if dispatch.status == 'returned' else ''
            values = (dispatch.id, dispatch.dc_number, dispatch.customer_name, dispatch.cylinder_id_text,
                      dispatch.cylinder_type, dispatch.grade or '', dispatch.dispatch_date, dispatch.return_date, dispatch.status, delete_text)
            self.tree.insert('', tk.END, values=values)

        # Update DC combo with unique DC numbers that have dispatched cylinders
        dc_numbers = list(set(d[1] for d in self.dispatches if d[8] == 'dispatched'))
        dc_numbers.sort(reverse=True)
        self.dc_combo['values'] = dc_numbers

        # Update DC filter combo
        all_dc_numbers = list(set(d[1] for d in self.dispatches))
        all_dc_numbers.sort(reverse=True)
        self.dc_filter_combo['values'] = ["All"] + all_dc_numbers

        # Apply current filters
        self.on_filter_change()

    def generate_bill(self):
        """Generate a bill for the selected company and DC."""
        company_selection = self.company_filter_var.get()
        dc_selection = self.dc_filter_var.get()

        if company_selection == "All":
            messagebox.showerror("Error", "Please select a specific company to generate bill.")
            return

        customer_id = int(company_selection.split(' - ')[0])
        customer_name = company_selection.split(' - ')[1]

        # Get dispatches for this customer, optionally filtered by DC
        conn = get_connection()
        cursor = conn.cursor()
        if dc_selection == "All":
            cursor.execute('''
                SELECT d.dc_number, d.dispatch_date, d.return_date, d.status, cy.cylinder_id, cy.cylinder_type, d.dispatch_notes
                FROM dispatches d
                JOIN cylinders cy ON d.cylinder_id = cy.id
                WHERE d.customer_id = ?
                ORDER BY d.dispatch_date DESC
            ''', (customer_id,))
        else:
            cursor.execute('''
                SELECT d.dc_number, d.dispatch_date, d.return_date, d.status, cy.cylinder_id, cy.cylinder_type, d.dispatch_notes
                FROM dispatches d
                JOIN cylinders cy ON d.cylinder_id = cy.id
                WHERE d.customer_id = ? AND d.dc_number = ?
                ORDER BY d.dispatch_date DESC
            ''', (customer_id, dc_selection))
        dispatches = cursor.fetchall()
        conn.close()

        if not dispatches:
            messagebox.showinfo("No Data", f"No dispatches found for {customer_name}.")
            return

        # Generate bill text
        bill_title = f"Bill for {customer_name}"
        if dc_selection != "All":
            bill_title += f" - DC {dc_selection}"
        bill_text = f"{bill_title}\n"
        bill_text += "=" * 50 + "\n\n"
        bill_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        total_cylinders = 0
        dispatched_count = 0
        returned_count = 0

        for dc, disp_date, ret_date, status, cyl_id, cyl_type, notes in dispatches:
            bill_text += f"DC Number: {dc}\n"
            bill_text += f"Cylinder: {cyl_id} ({cyl_type})\n"
            bill_text += f"Dispatch Date: {disp_date}\n"
            if ret_date:
                bill_text += f"Return Date: {ret_date}\n"
            bill_text += f"Status: {status}\n"
            if notes:
                bill_text += f"Notes: {notes}\n"
            bill_text += "-" * 30 + "\n"

            total_cylinders += 1
            if status == 'dispatched':
                dispatched_count += 1
            elif status == 'returned':
                returned_count += 1

        bill_text += f"\nSummary:\n"
        bill_text += f"Total Cylinders: {total_cylinders}\n"
        bill_text += f"Currently Dispatched: {dispatched_count}\n"
        bill_text += f"Returned: {returned_count}\n"

        # Show bill in a new window
        bill_window = tk.Toplevel(self)
        bill_window.title(bill_title)
        bill_window.geometry("600x400")

        text_widget = tk.Text(bill_window, wrap=tk.WORD)
        text_widget.insert(tk.END, bill_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Save button
        def save_bill():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Bill"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(bill_text)
                messagebox.showinfo("Success", f"Bill saved to {file_path}")

        tk.Button(bill_window, text="Save Bill", command=save_bill).pack(pady=5)

    def export_to_excel(self):
        """Export the current dispatch history to Excel."""
        if Workbook is None:
            messagebox.showerror("Error", "openpyxl is not installed. Cannot export to Excel.")
            return

        # Default filename based on selected company and date
        company_selection = self.company_filter_var.get()
        if company_selection == "All":
            default_name = f"Dispatch_History_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        else:
            company_name = company_selection.split(' - ')[1].replace(' ', '_')
            default_name = f"{company_name}_Dispatch_History_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Dispatch History",
            initialfile=default_name
        )
        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Dispatch History"

            # Headers
            headers = ['ID', 'DC Number', 'Customer', 'Cylinder ID', 'Cylinder Type', 'Grade', 'Dispatch Date', 'Return Date', 'Status', 'Delete']
            for col_num, header in enumerate(headers, 1):
                ws.cell(row=1, column=col_num, value=header)

            # Data from treeview
            for row_num, item in enumerate(self.tree.get_children(), 2):
                values = self.tree.item(item, 'values')
                for col_num, value in enumerate(values, 1):
                    ws.cell(row=row_num, column=col_num, value=value)

            wb.save(file_path)
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    def on_filter_change(self, event=None):
        """Handle filter change."""
        filter_status = self.filter_var.get()
        filter_company = self.company_filter_var.get()
        filter_dc = self.dc_filter_var.get()
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered_dispatches = self.dispatches

        # Filter by status
        if filter_status != "All":
            filtered_dispatches = [d for d in filtered_dispatches if d[8] == filter_status]

        # Filter by company
        if filter_company != "All":
            company_id = int(filter_company.split(' - ')[0])
            filtered_dispatches = [d for d in filtered_dispatches if d[2] == company_id]

        # Filter by DC
        if filter_dc != "All":
            filtered_dispatches = [d for d in filtered_dispatches if d[1] == filter_dc]

        for dispatch_row in filtered_dispatches:
            dispatch = Dispatch.from_db_row(dispatch_row)
            delete_text = 'Delete' if dispatch.status == 'returned' else ''
            values = (dispatch.id, dispatch.dc_number, dispatch.customer_name, dispatch.cylinder_id_text,
                      dispatch.cylinder_type, dispatch.grade or '', dispatch.dispatch_date, dispatch.return_date, dispatch.status, delete_text)
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

    def resolve_cylinder_id(self, input_id):
        """Resolve input to cylinder database ID. Accepts ID or cylinder_id_text."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Try as integer ID
            try:
                cylinder_id = int(input_id)
                cursor.execute("SELECT id FROM cylinders WHERE id = ?", (cylinder_id,))
                result = cursor.fetchone()
                if result:
                    return cylinder_id
            except ValueError:
                pass

            # Try as cylinder_id_text
            cursor.execute("SELECT id FROM cylinders WHERE cylinder_id = ?", (input_id,))
            result = cursor.fetchone()
            if result:
                return result[0]

            return None
        finally:
            conn.close()

    def update_selected_cylinders(self):
        """Update the selected cylinders listbox with current selections."""
        self.selected_cylinders_listbox.delete(0, tk.END)

        selected_indices = self.cylinder_listbox.curselection()
        manual_cylinders = self.manual_cylinder_entry.get().strip()

        cylinder_ids = set()
        errors = []

        # From listbox (already available)
        for index in selected_indices:
            cylinder_text = self.cylinder_listbox.get(index)
            cylinder_id = int(cylinder_text.split(' - ')[0])
            cylinder_ids.add(cylinder_id)

        # From manual input
        if manual_cylinders:
            manual_ids = [id.strip() for id in manual_cylinders.split(',') if id.strip()]
            conn = get_connection()
            cursor = conn.cursor()
            for manual_id in manual_ids:
                resolved_id = self.resolve_cylinder_id(manual_id)
                if resolved_id is None:
                    errors.append(f"Invalid cylinder: {manual_id}")
                else:
                    cursor.execute("SELECT status, cylinder_id FROM cylinders WHERE id = ?", (resolved_id,))
                    result = cursor.fetchone()
                    if result:
                        status, cyl_id = result
                        if status == 'available':
                            cylinder_ids.add(resolved_id)
                        else:
                            errors.append(f"Cylinder {cyl_id} (ID: {resolved_id}) is not available (status: {status})")
                    else:
                        errors.append(f"Cylinder {manual_id} not found")
            conn.close()

        # Display errors if any
        if errors:
            error_msg = "Errors in manual cylinder input:\n" + "\n".join(errors)
            messagebox.showerror("Cylinder Selection Errors", error_msg)

        # Display valid cylinders
        if cylinder_ids:
            conn = get_connection()
            cursor = conn.cursor()
            for cylinder_id in sorted(cylinder_ids):
                cursor.execute("SELECT cylinder_id, cylinder_type FROM cylinders WHERE id = ?", (cylinder_id,))
                result = cursor.fetchone()
                if result:
                    self.selected_cylinders_listbox.insert(tk.END, f"{cylinder_id} - {result[0]} ({result[1]})")
            conn.close()

    def dispatch_cylinders(self):
        """Dispatch selected cylinders to a customer."""
        customer_selection = self.customer_var.get()
        selected_indices = self.cylinder_listbox.curselection()
        manual_cylinders = self.manual_cylinder_entry.get().strip()
        dispatch_date = self.dispatch_date_entry.get().strip()
        grade = self.grade_entry.get().strip()
        dispatch_notes = ""

        if not customer_selection:
            messagebox.showerror("Error", "Please select a customer.")
            return

        if not selected_indices and not manual_cylinders:
            messagebox.showerror("Error", "Please select cylinders from the list or enter manual cylinder IDs.")
            return

        if not dispatch_date:
            messagebox.showerror("Error", "Please enter dispatch date.")
            return

        try:
            # Extract customer ID
            customer_id = int(customer_selection.split(' - ')[0])

            # Extract cylinder IDs from listbox
            cylinder_ids = []
            for index in selected_indices:
                cylinder_text = self.cylinder_listbox.get(index)
                cylinder_id = int(cylinder_text.split(' - ')[0])
                cylinder_ids.append(cylinder_id)

            # Extract cylinder IDs from manual input
            if manual_cylinders:
                manual_ids = [id.strip() for id in manual_cylinders.split(',') if id.strip()]
                for manual_id in manual_ids:
                    resolved_id = self.resolve_cylinder_id(manual_id)
                    if resolved_id is None:
                        raise ValueError(f"Invalid cylinder ID or cylinder_id: {manual_id}")
                    cylinder_ids.append(resolved_id)

            # Remove duplicates
            cylinder_ids = list(set(cylinder_ids))

            dc_number = self.dc_number_var.get().strip()
            if not dc_number:
                dc_number = None  # Will generate new one
            dc_number = dispatch_cylinders(customer_id, cylinder_ids, dispatch_date, dispatch_notes, dc_number, grade)
            self.load_dispatches()
            self.load_available_cylinders()

            self.customer_var.set('')
            self.dc_number_var.set(self.generate_dc_number())  # Generate new DC number for next dispatch
            self.manual_cylinder_entry.delete(0, tk.END)
            self.grade_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Cylinders dispatched successfully under DC {dc_number}.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to dispatch cylinders: {e}")

    def on_tree_double_click(self, event):
        """Handle double-click on treeview for delete action."""
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        values = self.tree.item(item, 'values')
        if len(values) > 9 and values[9] == 'Delete':
            dispatch_id = values[0]
            # Confirm delete
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete dispatch record ID {dispatch_id}?"):
                try:
                    dispatch = Dispatch(id=dispatch_id)
                    dispatch.delete()
                    self.load_dispatches()
                    messagebox.showinfo("Success", "Dispatch record deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete dispatch record: {e}")

    def return_cylinders(self):
        """Return selected cylinders."""
        dc_number = self.dc_var.get()
        selected_indices = self.return_cylinder_listbox.curselection()
        return_date = self.return_date_entry.get().strip()
        return_notes = ""

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
            messagebox.showinfo("Success", "Cylinders returned successfully.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return cylinders: {e}")