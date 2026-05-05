"""
Script to add Hassan Science College CDC Staff data to database
"""
import re
from app import create_app
from models import db, User, Department
from werkzeug.security import generate_password_hash

cdc_staff_text = """
1
Jayalakshmi
2
Vasudeva
3
Jaya
4
Umesha
5
Rathnamma K R
6
Saroja
7
Dhanalakshmi
8
Malligamma
9
Prameela
10
Ashwini N C
11
Pallavi A S
12
Susheela
"""

def parse_cdc_staff(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    staff = []
    
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            name = lines[i+1].strip()
            staff.append({
                'name': name,
                'designation': 'CDC Staff'
            })
            
    return staff

app = create_app('development')

with app.app_context():
    print("Parsing CDC staff data...")
    staff_data = parse_cdc_staff(cdc_staff_text)
    
    # Get Administration department ID if exists
    admin_dept = Department.query.filter_by(name='Administration').first()
    if not admin_dept:
        admin_dept = Department(name='Administration')
        db.session.add(admin_dept)
        db.session.commit()
    
    added_count = 0
    for st in staff_data:
        # Create a simple username
        username = st['name'].lower().replace(' ', '_').replace('.', '')
        # Clean up multiple underscores
        username = re.sub(r'_+', '_', username).strip('_')
        
        # Check if exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            if existing.designation != st['designation']:
                existing.designation = st['designation']
                existing.role = 'Staff'
            continue
            
        user = User(
            username=username,
            email=f"{username}@gsc.edu.in",
            password_hash=generate_password_hash('Staff@123'),
            full_name=st['name'],
            role='Staff',
            designation=st['designation'],
            department_id=admin_dept.id,
            is_active=True
        )
        db.session.add(user)
        added_count += 1
        print(f"  Added: {st['name']} - {st['designation']}")
        
    db.session.commit()
    print(f"\nAdded {added_count} new CDC staff members to the database.")
    print("Now the chatbot and tracking system will recognize them.")
