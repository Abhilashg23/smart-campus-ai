"""
Create face_data table for face recognition
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app('development')

def create_face_data_table():
    """Create face_data table if it doesn't exist"""
    with app.app_context():
        print("Creating face_data table...")
        
        try:
            # Create all tables (will only create missing ones)
            db.create_all()
            print("✓ face_data table created successfully!")
            
            # Verify the table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'face_data' in tables:
                print(f"✓ Verified: face_data table exists")
                
                # Show table structure
                columns = inspector.get_columns('face_data')
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("✗ Error: face_data table was not created")
            
            print("\n" + "="*60)
            print("Database tables:")
            for table in tables:
                print(f"  - {table}")
            print("="*60)
            
        except Exception as e:
            print(f"Error creating face_data table: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    create_face_data_table()
