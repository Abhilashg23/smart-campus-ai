#!/usr/bin/env python3
"""
Create visitor_entries table for visitor management system
"""

from app import create_app
from models import db
from models.visitor_entry import VisitorEntry

def create_visitor_entry_table():
    """Create the visitor_entries table"""
    app = create_app('development')
    
    with app.app_context():
        # Create the table
        db.create_all()
        print("✓ visitor_entries table created successfully!")
        
        # Verify table creation
        inspector = db.inspect(db.engine)
        if 'visitor_entries' in inspector.get_table_names():
            print("✓ Table verified in database")
            
            # Show table columns
            columns = inspector.get_columns('visitor_entries')
            print(f"\nTable has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ Table creation failed")

if __name__ == '__main__':
    create_visitor_entry_table()
