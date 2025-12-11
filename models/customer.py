#!/usr/bin/env python3
"""
Customer model for Cylinder Management System
"""

class Customer:
    def __init__(self, id=None, name="", contact_info="", address="", notes="", created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.contact_info = contact_info
        self.address = address
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_db_row(cls, row):
        """Create Customer instance from database row."""
        return cls(
            id=row[0],
            name=row[1],
            contact_info=row[2],
            address=row[3],
            notes=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    def to_dict(self):
        """Convert to dictionary for display."""
        return {
            'ID': self.id,
            'Name': self.name,
            'Contact Info': self.contact_info,
            'Address': self.address,
            'Notes': self.notes
        }