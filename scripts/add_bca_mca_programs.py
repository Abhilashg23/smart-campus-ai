"""
Add BCA and MCA programs to the database
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Program, Department

app = create_app('development')

def add_bca_mca_programs():
    """Add BCA and MCA programs"""
    with app.app_context():
        print("Adding BCA and MCA programs...")
        
        # Get Computer Science/Engineering department
        cs_dept = Department.query.filter(
            (Department.name.like('%Engineering%')) | 
            (Department.name.like('%Computer%'))
        ).first()
        
        if not cs_dept:
            # Use School of Engineering
            cs_dept = Department.query.filter_by(name='School of Engineering').first()
        
        if not cs_dept:
            print("Error: No suitable department found for BCA/MCA programs")
            return
        
        print(f"Using department: {cs_dept.name}")
        
        # BCA and MCA programs
        programs_data = [
            # BCA Programs (3 years)
            {'name': 'BCA General', 'code': 'BCA-GEN', 'duration': 3},
            {'name': 'BCA Cybersecurity', 'code': 'BCA-CYBER', 'duration': 3},
            {'name': 'BCA Data Science', 'code': 'BCA-DS', 'duration': 3},
            
            # MCA Programs (2 years)
            {'name': 'MCA General', 'code': 'MCA-GEN', 'duration': 2},
            {'name': 'MCA Cybersecurity', 'code': 'MCA-CYBER', 'duration': 2},
            {'name': 'MCA Data Science', 'code': 'MCA-DS', 'duration': 2},
        ]
        
        added_count = 0
        skipped_count = 0
        
        for prog_data in programs_data:
            # Check if program already exists
            existing = Program.query.filter_by(code=prog_data['code']).first()
            if not existing:
                program = Program(
                    name=prog_data['name'],
                    code=prog_data['code'],
                    department_id=cs_dept.id,
                    duration_years=prog_data['duration']
                )
                db.session.add(program)
                print(f"  ✓ Added: {prog_data['name']}")
                added_count += 1
            else:
                print(f"  - Skipped (exists): {prog_data['name']}")
                skipped_count += 1
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print(f"✓ BCA/MCA programs migration completed!")
        print(f"  Programs added: {added_count}")
        print(f"  Programs skipped: {skipped_count}")
        print(f"  Total programs in database: {Program.query.count()}")
        print(f"{'='*60}")


if __name__ == "__main__":
    add_bca_mca_programs()
