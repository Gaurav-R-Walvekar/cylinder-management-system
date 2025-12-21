#!/usr/bin/env python3
"""
Database module for Cylinder Management System
Handles SQLite database operations and schema management.
"""

import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "cylinder_management.db"

def get_connection():
    """Get database connection."""
    return sqlite3.connect(DATABASE_FILE)

def generate_dc_number():
    """Generate a unique DC number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dispatches")
    count = cursor.fetchone()[0]
    conn.close()
    # Generate DC number like DC001, DC002, etc.
    return f"DC{count + 1:03d}"

def init_database():
    """Initialize database and create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT,
            address TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create cylinders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cylinders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cylinder_id TEXT UNIQUE NOT NULL,
            cylinder_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create dispatches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dc_number TEXT NOT NULL,
            customer_id INTEGER NOT NULL,
            cylinder_id INTEGER NOT NULL,
            dispatch_date DATE NOT NULL,
            return_date DATE,
            dispatch_notes TEXT,
            return_notes TEXT,
            status TEXT NOT NULL DEFAULT 'dispatched',
            grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (cylinder_id) REFERENCES cylinders (id)
        )
    ''')

    # Add grade column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE dispatches ADD COLUMN grade TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # For simplicity, using plain text password. In production, use hashing.
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                      ('admin', 'admin123', 'admin'))

    conn.commit()
    conn.close()

# Customer operations
def add_customer(name, contact_info, address, notes):
    """Add a new customer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (name, contact_info, address, notes)
        VALUES (?, ?, ?, ?)
    ''', (name, contact_info, address, notes))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def get_all_customers():
    """Get all customers."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY name")
    customers = cursor.fetchall()
    conn.close()
    return customers

def update_customer(customer_id, name, contact_info, address, notes):
    """Update customer information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE customers
        SET name = ?, contact_info = ?, address = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (name, contact_info, address, notes, customer_id))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    """Delete a customer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

def search_customers(query):
    """Search customers by name or contact info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM customers
        WHERE name LIKE ? OR contact_info LIKE ?
        ORDER BY name
    ''', (f'%{query}%', f'%{query}%'))
    customers = cursor.fetchall()
    conn.close()
    return customers

# Cylinder operations
def add_cylinder(cylinder_id, cylinder_type, status, location):
    """Add a new cylinder."""
    if not cylinder_id or not cylinder_type:
        raise ValueError("Cylinder ID and type are required")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO cylinders (cylinder_id, cylinder_type, status, location)
            VALUES (?, ?, ?, ?)
        ''', (cylinder_id, cylinder_type, status, location))
        cylinder_db_id = cursor.lastrowid
        conn.commit()
        return cylinder_db_id
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError(f"Cylinder ID '{cylinder_id}' already exists")
        raise
    finally:
        conn.close()

def get_all_cylinders():
    """Get all cylinders."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cylinders ORDER BY cylinder_id")
    cylinders = cursor.fetchall()
    conn.close()
    return cylinders

def update_cylinder(cylinder_id, cylinder_type, status, location):
    """Update cylinder information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE cylinders
        SET cylinder_type = ?, status = ?, location = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (cylinder_type, status, location, cylinder_id))
    conn.commit()
    conn.close()

def delete_cylinder(cylinder_id):
    """Delete a cylinder."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cylinders WHERE id = ?", (cylinder_id,))
    conn.commit()
    conn.close()

def search_cylinders(query):
    """Search cylinders by ID, type, or status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM cylinders
        WHERE cylinder_id LIKE ? OR cylinder_type LIKE ? OR status LIKE ?
        ORDER BY cylinder_id
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    cylinders = cursor.fetchall()
    conn.close()
    return cylinders

def get_cylinders_by_status(status):
    """Get cylinders by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cylinders WHERE status = ? ORDER BY cylinder_id", (status,))
    cylinders = cursor.fetchall()
    conn.close()
    return cylinders

# Dispatch operations
def dispatch_cylinders(customer_id, cylinder_ids, dispatch_date, dispatch_notes, dc_number=None, grade=None):
    """Dispatch multiple cylinders to a customer with a DC number."""
    if not cylinder_ids:
        raise ValueError("At least one cylinder must be selected")

    # Validate date format
    try:
        datetime.strptime(dispatch_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid dispatch date format. Use YYYY-MM-DD")

    if not dc_number:
        dc_number = generate_dc_number()
    else:
        # Check if custom DC number already exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dispatches WHERE dc_number = ?", (dc_number,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            raise ValueError(f"DC number {dc_number} already exists. Please choose a different DC number.")

    try:
        # First, verify all cylinders are available
        for cylinder_id in cylinder_ids:
            cursor.execute("SELECT status FROM cylinders WHERE id = ?", (cylinder_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Cylinder with ID {cylinder_id} does not exist")
            if result[0] != 'available':
                raise ValueError(f"Cylinder {cylinder_id} is not available (current status: {result[0]})")

        # Now dispatch all cylinders
        for cylinder_id in cylinder_ids:
            cursor.execute('''
                INSERT INTO dispatches (dc_number, customer_id, cylinder_id, dispatch_date, dispatch_notes, status, grade)
                VALUES (?, ?, ?, ?, ?, 'dispatched', ?)
            ''', (dc_number, customer_id, cylinder_id, dispatch_date, dispatch_notes, grade))
            # Update cylinder status
            cursor.execute("UPDATE cylinders SET status = 'dispatched' WHERE id = ?", (cylinder_id,))
        conn.commit()
        return dc_number
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Database error during dispatch: {str(e)}")
    finally:
        conn.close()

def return_cylinders(dc_number, cylinder_ids, return_date, return_notes):
    """Return specific cylinders under a DC number."""
    if not cylinder_ids:
        raise ValueError("At least one cylinder must be selected for return")

    # Validate date format
    try:
        datetime.strptime(return_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid return date format. Use YYYY-MM-DD")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        for cylinder_id in cylinder_ids:
            # Check if cylinder is dispatched under this DC number
            cursor.execute("""
                SELECT id, status FROM dispatches
                WHERE dc_number = ? AND cylinder_id = ? AND status = 'dispatched'
            """, (dc_number, cylinder_id))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Cylinder {cylinder_id} is not dispatched under DC {dc_number} or already returned")

            dispatch_id = result[0]
            # Update dispatch
            cursor.execute('''
                UPDATE dispatches
                SET return_date = ?, return_notes = ?, status = 'returned'
                WHERE id = ?
            ''', (return_date, return_notes, dispatch_id))
            # Update cylinder status to returned
            cursor.execute("UPDATE cylinders SET status = 'returned' WHERE id = ?", (cylinder_id,))
        conn.commit()
    finally:
        conn.close()

def get_all_dispatches():
    """Get all dispatches with customer and cylinder info."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, d.dc_number, d.customer_id, d.cylinder_id, d.dispatch_date, d.return_date, d.dispatch_notes, d.return_notes, d.status, d.grade, d.created_at, c.name as customer_name, cy.cylinder_id as cylinder_id_text, cy.cylinder_type as cylinder_type
        FROM dispatches d
        JOIN customers c ON d.customer_id = c.id
        JOIN cylinders cy ON d.cylinder_id = cy.id
        ORDER BY d.dc_number DESC, d.dispatch_date DESC
    ''')
    dispatches = cursor.fetchall()
    conn.close()
    return dispatches

def get_dispatches_by_dc(dc_number):
    """Get all dispatches for a specific DC number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, d.dc_number, d.customer_id, d.cylinder_id, d.dispatch_date, d.return_date, d.dispatch_notes, d.return_notes, d.status, d.grade, d.created_at, c.name as customer_name, cy.cylinder_id as cylinder_id_text, cy.cylinder_type as cylinder_type
        FROM dispatches d
        JOIN customers c ON d.customer_id = c.id
        JOIN cylinders cy ON d.cylinder_id = cy.id
        WHERE d.dc_number = ?
        ORDER BY d.dispatch_date DESC
    ''', (dc_number,))
    dispatches = cursor.fetchall()
    conn.close()
    return dispatches

def get_dispatched_cylinders_by_dc(dc_number):
    """Get cylinders currently dispatched under a DC number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cy.id, cy.cylinder_id
        FROM dispatches d
        JOIN cylinders cy ON d.cylinder_id = cy.id
        WHERE d.dc_number = ? AND d.status = 'dispatched'
    ''', (dc_number,))
    cylinders = cursor.fetchall()
    conn.close()
    return cylinders

def get_dispatches_by_customer(customer_id):
    """Get dispatches for a specific customer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.id, d.dc_number, d.customer_id, d.cylinder_id, d.dispatch_date, d.return_date, d.dispatch_notes, d.return_notes, d.status, d.grade, d.created_at, cy.cylinder_id as cylinder_id_text
        FROM dispatches d
        JOIN cylinders cy ON d.cylinder_id = cy.id
        WHERE d.customer_id = ?
        ORDER BY d.dispatch_date DESC
    ''', (customer_id,))
    dispatches = cursor.fetchall()
    conn.close()
    return dispatches

# Authentication
def authenticate_user(username, password):
    """Authenticate user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
