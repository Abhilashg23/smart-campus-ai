"""
Database migration script to create student_tracking table
Run this script to create the new table for student entry/exit tracking
"""

from app import create_app
from models import db
from models.student_tracking import StudentTracking

def create_tracking_table():
    """Create the student_tracking table"""
    app = create_app('development')
    with app.app_context():
        # Create the table
        db.create_all()
        print("✓ Student tracking table created successfully!")
        print("  - Table: student_tracking")
        print("  - Columns: id, user_id, entry_type, timestamp, verification_method, location")

if __name__ == '__main__':
    create_tracking_table()

