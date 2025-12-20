#!/usr/bin/env python3
"""
Login screen for Cylinder Management System
"""

import tkinter as tk
from tkinter import messagebox
from database import authenticate_user

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.root = tk.Tk()
        self.root.title("Cylinder Management System - Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Center the window
        self.root.eval('tk::PlaceWindow . center')

        self.create_widgets()

    def create_widgets(self):
        """Create login form widgets."""
        # Set window background
        self.root.configure(bg='#f0f0f0')

        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=40)

        # Title
        title_label = tk.Label(main_frame, text="Cylinder Management System",
                              font=("Arial", 16, "bold"), fg='#2c3e50', bg='#f0f0f0')
        title_label.pack(pady=(10, 5))

        subtitle_label = tk.Label(main_frame, text="Please enter your credentials",
                                 font=("Arial", 9), fg='#7f8c8d', bg='#f0f0f0')
        subtitle_label.pack(pady=(0, 25))

        # Login frame
        login_frame = tk.LabelFrame(main_frame, text="Login", font=("Arial", 11, "bold"),
                                   bg='white', fg='#2c3e50', relief='solid', bd=1)
        login_frame.pack(pady=10, padx=20)

        # Username
        tk.Label(login_frame, text="Username:", font=("Arial", 10),
                bg='white', fg='#2c3e50').grid(row=0, column=0, pady=15, padx=20, sticky="e")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 10), width=25,
                                      relief='solid', bd=1)
        self.username_entry.grid(row=0, column=1, pady=15, padx=20)
        self.username_entry.focus()

        # Password
        tk.Label(login_frame, text="Password:", font=("Arial", 10),
                bg='white', fg='#2c3e50').grid(row=1, column=0, pady=15, padx=20, sticky="e")
        self.password_entry = tk.Entry(login_frame, font=("Arial", 10), width=25, show="*",
                                      relief='solid', bd=1)
        self.password_entry.grid(row=1, column=1, pady=15, padx=20)

        # Login button
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=25)

        login_button = tk.Button(button_frame, text="Login", font=("Arial", 11, "bold"),
                                bg='#3498db', fg='white', relief='raised', bd=2,
                                padx=35, pady=8, command=self.login,
                                activebackground='#2980b9', activeforeground='white')
        login_button.pack()

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())

    def run(self):
        """Start the login window."""
        self.root.mainloop()

    def login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        user = authenticate_user(username, password)
        if user:
            self.root.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")