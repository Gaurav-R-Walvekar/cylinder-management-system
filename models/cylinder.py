#!/usr/bin/env python3
"""
Cylinder model for Cylinder Management System
"""

class Cylinder:
    def __init__(self, id=None, cylinder_id="", cylinder_type="", status="available", location="", created_at=None, updated_at=None):
        self.id = id
        self.cylinder_id = cylinder_id
        self.cylinder_type = cylinder_type
        self.status = status
        self.location = location
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_db_row(cls, row):
        """Create Cylinder instance from database row."""
        return cls(
            id=row[0],
            cylinder_id=row[1],
            cylinder_type=row[2],
            status=row[3],
            location=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    def to_dict(self):
        """Convert to dictionary for display."""
        return {
            'ID': self.id,
            'Cylinder ID': self.cylinder_id,
            'Type': self.cylinder_type,
            'Status': self.status,
            'Location': self.location
        }