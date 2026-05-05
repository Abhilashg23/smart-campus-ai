"""
Script to add Hassan Science College Non-Teaching Staff data to database
"""
import re
from app import create_app
from models import db, User, Department
from werkzeug.security import generate_password_hash

staff_text = """
1	KIRANA  H  M 	GAZETTED MANAGER 
2	NALINAKSHI   K 	GAZETTED MANAGER (Deputation)
3	GEETHAMANI  C  D	SUPERINTENDENT 
4	SHREELAKSHMI  H Y	FIRST DIVISION ASSISTANT
5	MANJUNATHA   H A	FIRST DIVISION ASSISTANT
6	SAROJAMMA  K T	SECOND DIVISION ASSISTANT
7	SAHANA  H  R	SECOND DIVISION ASSISTANT
8	LEELAVATHI  H C	ATTENDER 
9	MAMATHA  H  S	ATTENDER 
10	SUSHIL KUMAR  S	ATTENDER 
11	PRAKASH  H  S	ATTENDER 
12	KUMAR H  D	ATTENDER 
"""

def parse_staff(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    staff_list = []
    
    for line in lines:
        parts = re.split(r'\t+', line)
        if len(parts) >= 3:
            name = parts[1].strip()
            designation = parts[2].strip()
            staff_list.append({
                'name': name,
                'designation': designation
            })
            
    return staff_list

app = create_app('development')

with app.app_context():
    print("Parsing staff data...")
    staff_data = parse_staff(staff_text)
    
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
    print(f"\nAdded {added_count} new staff members to the database.")
    print("Now the chatbot and tracking system will recognize them.")
