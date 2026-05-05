"""
Database migration script to add student-specific fields to User model
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app('development')

def migrate_database():
    """Add student-specific fields to users table"""
    with app.app_context():
        print("Running database migration for student fields...")
        print("Adding student-specific fields to users table...")
        
        try:
            # Add columns using raw SQL
            with db.engine.connect() as conn:
                # Check if columns already exist
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]
                
                columns_to_add = [
                    ("first_name", "VARCHAR(100)"),
                    ("last_name", "VARCHAR(100)"),
                    ("registration_id", "VARCHAR(50)"),  # UNIQUE constraint added via index below
                    ("year", "INTEGER"),
                    ("section", "VARCHAR(10)")
                ]
                
                for column_name, column_type in columns_to_add:
                    if column_name not in existing_columns:
                        print(f"Adding column: {column_name}")
                        conn.execute(db.text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                        conn.commit()
                    else:
                        print(f"Column {column_name} already exists, skipping...")
                
                # Create index on registration_id if it doesn't exist
                try:
                    conn.execute(db.text("CREATE INDEX IF NOT EXISTS idx_registration_id ON users(registration_id)"))
                    conn.commit()
                    print("Created index on registration_id")
                except:
                    pass
                
                print("\n✓ Database migration completed successfully!")
                return True
                
        except Exception as e:
            print(f"\n✗ Migration error: {str(e)}")
            return False


if __name__ == "__main__":
    migrate_database()
