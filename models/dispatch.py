#!/usr/bin/env python3
"""
Dispatch model for Cylinder Management System
"""

class Dispatch:
    def __init__(self, id=None, dc_number="", customer_id=None, cylinder_id=None, dispatch_date=None, return_date=None,
                 dispatch_notes="", return_notes="", status="dispatched", created_at=None,
                 customer_name="", cylinder_id_text="", cylinder_type=""):
        self.id = id
        self.dc_number = dc_number
        self.customer_id = customer_id
        self.cylinder_id = cylinder_id
        self.dispatch_date = dispatch_date
        self.return_date = return_date
        self.dispatch_notes = dispatch_notes
        self.return_notes = return_notes
        self.status = status
        self.created_at = created_at
        self.customer_name = customer_name
        self.cylinder_id_text = cylinder_id_text
        self.cylinder_type = cylinder_type

    @classmethod
    def from_db_row(cls, row):
        """Create Dispatch instance from database row."""
        return cls(
            id=row[0],
            dc_number=row[1],
            customer_id=row[2],
            cylinder_id=row[3],
            dispatch_date=row[4],
            return_date=row[5],
            dispatch_notes=row[6],
            return_notes=row[7],
            status=row[8],
            created_at=row[9],
            customer_name=row[10],
            cylinder_id_text=row[11],
            cylinder_type=row[12]
        )

    def to_dict(self):
        """Convert to dictionary for display."""
        return {
            'ID': self.id,
            'DC Number': self.dc_number,
            'Customer': self.customer_name,
            'Cylinder ID': self.cylinder_id_text,
            'Cylinder Type': self.cylinder_type,
            'Dispatch Date': self.dispatch_date,
            'Return Date': self.return_date,
            'Status': self.status,
            'Dispatch Notes': self.dispatch_notes,
            'Return Notes': self.return_notes
        }