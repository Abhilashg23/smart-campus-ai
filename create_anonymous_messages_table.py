#!/usr/bin/env python3
"""
Create anonymous_messages table in the database
"""
from app import create_app
from models import db
from models.anonymous_message import AnonymousMessage

def create_anonymous_messages_table():
    """Create the anonymous_messages table"""
    app = create_app('development')
    
    with app.app_context():
        # Create the table
        db.create_all()
        print("✅ Anonymous messages table created successfully!")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'anonymous_messages' in tables:
            print("✅ Table 'anonymous_messages' verified in database")
            
            # Show table columns
            columns = inspector.get_columns('anonymous_messages')
            print("\nTable columns:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")
        else:
            print("❌ Table 'anonymous_messages' not found in database")

if __name__ == '__main__':
    create_anonymous_messages_table()
