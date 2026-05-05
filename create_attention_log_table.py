"""
Database migration script to create attention_log table
Run this script once to set up the attention monitoring feature
"""

from app import create_app
from models import db
from models.attention_log import AttentionLog

def create_attention_log_table():
    """Create the attention_log table"""
    app = create_app()
    
    with app.app_context():
        # Check if table already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'attention_log' in existing_tables:
            print("✓ AttentionLog table already exists")
        else:
            # Create only the AttentionLog table
            AttentionLog.__table__.create(db.engine, checkfirst=True)
            print("✓ AttentionLog table created successfully!")
        
        # Verify table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'attention_log' in tables:
            print("✓ Verified: attention_log table exists in database")
            
            # Show table columns
            columns = inspector.get_columns('attention_log')
            print("\nTable columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ Error: attention_log table not found")

if __name__ == '__main__':
    create_attention_log_table()
