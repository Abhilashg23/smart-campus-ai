"""
Database migration script to add faculty fields to User model
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app('development')

def migrate_database():
    """Add new faculty fields to users table"""
    with app.app_context():
        print("Running database migration...")
        print("Adding faculty-specific fields to users table...")
        
        try:
            # Add columns using raw SQL (since we're not using Flask-Migrate)
            with db.engine.connect() as conn:
                # Check if columns already exist
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]
                
                columns_to_add = [
                    ("profile_image", "VARCHAR(500)"),
                    ("designation", "VARCHAR(200)"),
                    ("specialization", "TEXT"),
                    ("education", "TEXT"),
                    ("bio", "TEXT"),
                    ("research_interests", "TEXT"),
                    ("publications", "TEXT"),
                    ("university_profile_url", "VARCHAR(500)")
                ]
                
                for column_name, column_type in columns_to_add:
                    if column_name not in existing_columns:
                        print(f"Adding column: {column_name}")
                        conn.execute(db.text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                        conn.commit()
                    else:
                        print(f"Column {column_name} already exists, skipping...")
                
                print("\n✓ Database migration completed successfully!")
                return True
                
        except Exception as e:
            print(f"\n✗ Migration error: {str(e)}")
            return False


if __name__ == "__main__":
    migrate_database()
