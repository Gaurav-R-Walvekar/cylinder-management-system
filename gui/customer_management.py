#!/usr/bin/env python3
"""
Customer Management Frame for Cylinder Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import add_customer, get_all_customers, update_customer, delete_customer, search_customers
from models.customer import Customer

class CustomerManagementFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.customers = []
        self.create_widgets()
        self.load_customers()

    def create_widgets(self):
        """Create customer management widgets."""
        # Title
        title_label = tk.Label(self, text="Customer Management",
                              font=("Arial", 14, "bold"), fg='#2c3e50', bg='#f8f8f8')
        title_label.pack(pady=10)

        # Search frame
        search_frame = tk.LabelFrame(self, text="Search & Filter",
                                    font=("Arial", 10, "bold"), bg='#f8f9fa',
                                    fg='#2c3e50', relief='solid', bd=1)
        search_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(search_frame, text="Search Customers:", font=("Arial", 9),
                bg='#f8f9fa', fg='#2c3e50').pack(side=tk.LEFT, padx=10, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=35,
                                    font=("Arial", 9), relief='solid', bd=1)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)

        # Buttons frame
        buttons_frame = tk.Frame(self, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Button(buttons_frame, text="Add Customer", font=("Arial", 9, "bold"),
                 bg='#4CAF50', fg='white', relief='raised', bd=1, padx=15, pady=5,
                 command=self.add_customer).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Edit Customer", font=("Arial", 9, "bold"),
                 bg='#FF9800', fg='white', relief='raised', bd=1, padx=15, pady=5,
                 command=self.edit_customer).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Delete Customer", font=("Arial", 9, "bold"),
                 bg='#F44336', fg='white', relief='raised', bd=1, padx=15, pady=5,
                 command=self.delete_customer).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="Refresh", font=("Arial", 9, "bold"),
                 bg='#2196F3', fg='white', relief='raised', bd=1, padx=15, pady=5,
                 command=self.load_customers).pack(side=tk.LEFT, padx=5)

        # Customer list frame
        list_frame = tk.LabelFrame(self, text="Customer List",
                                  font=("Arial", 10, "bold"), bg='#ffffff',
                                  fg='#2c3e50', relief='solid', bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Treeview for customers
        columns = ('ID', 'Name', 'Contact Info', 'Address', 'Notes')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)

        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))

        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=60, anchor='center')
            elif col == 'Name':
                self.tree.column(col, width=150)
            elif col == 'Contact Info':
                self.tree.column(col, width=150)
            elif col == 'Address':
                self.tree.column(col, width=200)
            else:  # Notes
                self.tree.column(col, width=200)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Instructions label
        instruction_label = tk.Label(list_frame,
                                   text="Double-click on a customer to edit",
                                   font=("Arial", 8), fg='#7f8c8d', bg='#ffffff')
        instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self.edit_customer())

    def load_customers(self):
        """Load customers from database."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.customers = get_all_customers()
        for customer_row in self.customers:
            customer = Customer.from_db_row(customer_row)
            values = (customer.id, customer.name, customer.contact_info, customer.address, customer.notes)
            self.tree.insert('', tk.END, values=values)

    def on_search(self, event=None):
        """Handle search functionality."""
        query = self.search_var.get().strip()
        if query:
            # Clear current items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Load search results
            search_results = search_customers(query)
            for customer_row in search_results:
                customer = Customer.from_db_row(customer_row)
                values = (customer.id, customer.name, customer.contact_info, customer.address, customer.notes)
                self.tree.insert('', tk.END, values=values)
        else:
            self.load_customers()

    def add_customer(self):
        """Add new customer dialog."""
        dialog = CustomerDialog(self, "Add Customer")
        if dialog.result:
            try:
                name, contact_info, address, notes = dialog.result
                if not name.strip():
                    messagebox.showerror("Error", "Customer name is required.")
                    return
                add_customer(name, contact_info, address, notes)
                self.load_customers()
                messagebox.showinfo("Success", "Customer added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {e}")

    def edit_customer(self):
        """Edit selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a customer to edit.")
            return

        item = self.tree.item(selected_item[0])
        customer_id = item['values'][0]

        # Find customer data
        customer_data = None
        for row in self.customers:
            if row[0] == customer_id:
                customer_data = Customer.from_db_row(row)
                break

        if customer_data:
            dialog = CustomerDialog(self, "Edit Customer", customer_data)
            if dialog.result:
                try:
                    name, contact_info, address, notes = dialog.result
                    if not name.strip():
                        messagebox.showerror("Error", "Customer name is required.")
                        return
                    update_customer(customer_id, name, contact_info, address, notes)
                    self.load_customers()
                    messagebox.showinfo("Success", "Customer updated successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update customer: {e}")

    def delete_customer(self):
        """Delete selected customer."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a customer to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?"):
            return

        item = self.tree.item(selected_item[0])
        customer_id = item['values'][0]

        try:
            delete_customer(customer_id)
            self.load_customers()
            messagebox.showinfo("Success", "Customer deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {e}")

class CustomerDialog:
    """Dialog for adding/editing customers."""
    def __init__(self, parent, title, customer=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets(customer)
        self.dialog.wait_window()

    def create_widgets(self, customer):
        """Create dialog widgets."""
        # Labels and entries
        tk.Label(self.dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.dialog, width=40, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.dialog, text="Contact Info:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.contact_entry = tk.Entry(self.dialog, width=40, font=("Arial", 10))
        self.contact_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.dialog, text="Address:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.address_entry = tk.Text(self.dialog, width=30, height=3, font=("Arial", 10))
        self.address_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.dialog, text="Notes:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.notes_entry = tk.Text(self.dialog, width=30, height=3, font=("Arial", 10))
        self.notes_entry.grid(row=3, column=1, padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Save", font=("Arial", 10, "bold"),
                 bg='#4CAF50', fg='white', relief='raised', bd=1, padx=20, pady=5,
                 command=self.save).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Cancel", font=("Arial", 10, "bold"),
                 bg='#9E9E9E', fg='white', relief='raised', bd=1, padx=20, pady=5,
                 command=self.cancel).pack(side=tk.LEFT, padx=10)

        # Populate fields if editing
        if customer:
            self.name_entry.insert(0, customer.name)
            self.contact_entry.insert(0, customer.contact_info)
            self.address_entry.insert(tk.END, customer.address)
            self.notes_entry.insert(tk.END, customer.notes)

    def save(self):
        """Save customer data."""
        name = self.name_entry.get().strip()
        contact_info = self.contact_entry.get().strip()
        address = self.address_entry.get("1.0", tk.END).strip()
        notes = self.notes_entry.get("1.0", tk.END).strip()

        self.result = (name, contact_info, address, notes)
        self.dialog.destroy()

    def cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()