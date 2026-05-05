"""
Database migration script to add Program model and semester field
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Program, Department

app = create_app('development')

def migrate_database():
    """Add Program table and semester field to users table"""
    with app.app_context():
        print("Running database migration for programs and semester...")
        
        try:
            # Add columns using raw SQL
            with db.engine.connect() as conn:
                # Check if columns already exist
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]
                
                # Add program_id and semester if they don't exist
                if 'program_id' not in existing_columns:
                    print("Adding column: program_id")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN program_id INTEGER"))
                    conn.commit()
                else:
                    print("Column program_id already exists, skipping...")
                
                if 'semester' not in existing_columns:
                    print("Adding column: semester")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN semester INTEGER"))
                    conn.commit()
                else:
                    print("Column semester already exists, skipping...")
                
                print("\n✓ User table migration completed!")
                
            # Create programs table
            print("\nCreating programs table...")
            db.create_all()
            print("✓ Programs table created!")
            
            # Add sample programs for each department
            print("\nAdding sample programs...")
            departments = Department.query.all()
            
            programs_data = {
                'School of Engineering': [
                    {'name': 'B.Tech Computer Science Engineering', 'code': 'BTECH-CSE'},
                    {'name': 'B.Tech Electronics and Communication Engineering', 'code': 'BTECH-ECE'},
                    {'name': 'B.Tech Mechanical Engineering', 'code': 'BTECH-MECH'},
                    {'name': 'B.Tech Civil Engineering', 'code': 'BTECH-CIVIL'},
                    {'name': 'B.Tech Electrical Engineering', 'code': 'BTECH-EE'},
                ],
                'School of Management': [
                    {'name': 'MBA General Management', 'code': 'MBA-GM'},
                    {'name': 'MBA Finance', 'code': 'MBA-FIN'},
                    {'name': 'MBA Marketing', 'code': 'MBA-MKT'},
                    {'name': 'MBA Human Resources', 'code': 'MBA-HR'},
                ],
                'School of Sciences': [
                    {'name': 'B.Sc Physics', 'code': 'BSC-PHY'},
                    {'name': 'B.Sc Chemistry', 'code': 'BSC-CHEM'},
                    {'name': 'B.Sc Mathematics', 'code': 'BSC-MATH'},
                    {'name': 'B.Sc Biology', 'code': 'BSC-BIO'},
                ],
                'School of Arts': [
                    {'name': 'BA English Literature', 'code': 'BA-ENG'},
                    {'name': 'BA History', 'code': 'BA-HIST'},
                    {'name': 'BA Political Science', 'code': 'BA-POL'},
                ],
            }
            
            for dept in departments:
                if dept.name in programs_data:
                    for prog_data in programs_data[dept.name]:
                        # Check if program already exists
                        existing = Program.query.filter_by(code=prog_data['code']).first()
                        if not existing:
                            program = Program(
                                name=prog_data['name'],
                                code=prog_data['code'],
                                department_id=dept.id,
                                duration_years=4 if 'B.Tech' in prog_data['name'] or 'B.Sc' in prog_data['name'] or 'BA' in prog_data['name'] else 2
                            )
                            db.session.add(program)
                            print(f"  Added: {prog_data['name']}")
                        else:
                            print(f"  Skipped (exists): {prog_data['name']}")
            
            db.session.commit()
            print("\n✓ Database migration completed successfully!")
            return True
                
        except Exception as e:
            print(f"\n✗ Migration error: {str(e)}")
            return False


if __name__ == "__main__":
    migrate_database()
