#!/usr/bin/env python3
"""
Main window for Cylinder Management System
Contains navigation tabs for different screens.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.login import LoginWindow
from gui.customer_management import CustomerManagementFrame
from gui.inventory_management import InventoryManagementFrame
from gui.dispatch_tracking import DispatchTrackingFrame

class MainWindow:
    def __init__(self):
        self.root = None
        self.notebook = None
        self.frames = {}
        self.customer_frame = None
        self.inventory_frame = None
        self.dispatch_frame = None

    def show_login(self):
        """Show login window."""
        login_window = LoginWindow(self.show_main_window)
        login_window.run()

    def show_main_window(self):
        """Show main application window after successful login."""
        self.root = tk.Tk()
        self.root.title("Cylinder Management System")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximize window

        # Set application style
        self.style = ttk.Style()
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[15, 8])
        self.style.configure('TFrame', background='#f8f8f8')
        self.style.configure('TLabel', background='#f8f8f8', font=('Arial', 9))
        self.style.configure('TButton', font=('Arial', 9, 'bold'), padding=[8, 4])

        # Set main window background
        self.root.configure(bg='#f0f0f0')

        # Create menu bar
        self.create_menu_bar()

        # Create header frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="Cylinder Management System",
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=12)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create frames for each tab
        self.create_customer_tab()
        self.create_inventory_tab()
        self.create_dispatch_tab()

        # Bind tab change event to refresh data
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu_bar(self):
        """Create menu bar with logout option."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

    def create_customer_tab(self):
        """Create customer management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Customer Management")

        self.customer_frame = CustomerManagementFrame(frame)
        self.customer_frame.pack(fill=tk.BOTH, expand=True)

    def create_inventory_tab(self):
        """Create inventory management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventory Management")

        self.inventory_frame = InventoryManagementFrame(frame)
        self.inventory_frame.pack(fill=tk.BOTH, expand=True)

    def create_dispatch_tab(self):
        """Create dispatch tracking tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dispatch & Returns")

        self.dispatch_frame = DispatchTrackingFrame(frame)
        self.dispatch_frame.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        """Handle logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            self.show_login()

    def on_tab_changed(self, event):
        """Handle tab change event to refresh data."""
        current_tab = self.notebook.index(self.notebook.select())
        tab_text = self.notebook.tab(current_tab, "text")

        if tab_text == "Inventory Management" and self.inventory_frame:
            # Refresh inventory frame data
            self.inventory_frame.load_cylinders()
        elif tab_text == "Dispatch & Returns" and self.dispatch_frame:
            # Refresh dispatch frame data
            self.dispatch_frame.load_customers()
            self.dispatch_frame.load_available_cylinders()
            self.dispatch_frame.load_dispatches()

    def on_closing(self):
        """Handle window close event."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def run(self):
        """Start the application with login screen."""
        self.show_login()
        if self.root:
            self.root.mainloop()