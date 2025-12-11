#!/usr/bin/env python3
"""
Cylinder Management System - Main Entry Point
A desktop application for tracking cylinders, customers, and dispatches.
"""

import sys
import os
from gui.main_window import MainWindow
from database import init_database

def main():
    """Main application entry point."""
    try:
        # Initialize database
        init_database()

        # Create and run the main window
        app = MainWindow()
        app.run()

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()