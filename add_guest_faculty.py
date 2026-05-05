"""
Script to add Hassan Science College Guest Faculty data to database
"""
import re
from app import create_app
from models import db, User, Department
from werkzeug.security import generate_password_hash

guest_faculty_text = """
1
ARCHANA
Biotechnology
2
ARCHANA G S
Biotechnology
3
SUNITHA.R
Biotechnology
4
MANJU K
Botany
5
MANASA C R
Botany
6
SANDHYA G C
Chemistry
7
 MADHU M B
Chemistry
8
Dr. Shruthi E
Chemistry
9
Rashmi.R
Chemistry
10
AmreenAfshan
Chemistry
11
Mamatha C
Computer Science
12
Halesh Kumar N R
Computer Science
13
KAVYA R M
Computer Science
14
Preethi D
Computer Science
15
Rachitha J C
Computer Science
16
Deepika H M
Computer Science
17
Santhosh Kumar N R
Computer Science
18
NAVYA D
Computer Science
19
DARSHAN SJ
Computer Science
20
Abhilasha G P
Computer Science
21
Rashmi R.C
Computer Science
22
Sangeetha S
Computer Science
23
Puneeth R
Computer Science
24
Manjunath D
Computer Science
25
Smitha r p
Computer Science
26
D SAHANASHREE
Computer Science
27
HARSHITHA K S
Computer Science
28
SINDHU K G
Computer Science
29
MANASA S
Computer Science
30
ANOOP J
Computer Science
31
Vathsala S
Computer Science
32
Shambhavi V N
Computer Science
33
NITHYANANDA M D
Computer Science
34
Pavana MH
Computer Science
35
MANJUNATHA K L
Computer Science
36
Seema N
Computer Science
37
BHUVANESHWARI M
Computer Science
38
ROOPA G R
Computer Science
39
KAVITHA R
Computer Science
40
Jayaprakash H R
Computer Science
41
VIKRAM B.
Computer Science
42
Shruthi G G
Computer Science
43
ARUNDHATHI H M
Electronics
44
BHOJEGOWDA H P
English (Language and Optional)
45
CHETHANA R
English (Language and Optional)
46
VEENA D S
Hindi (Language and Optional)
47
Dr. YOGESHA N E
History
48
NATARAJA S
Journalism
49
DUMMEGOWDA T
Kannada (Language and Optional)
50
NIRANJAN K E
Kannada (Language and Optional)
51
ABHILASHA C D
Mathematics
52
SYED KHAN F. M.
Mathematics
53
MADHUSOODANA S H
Mathematics
54
BHAVYASHREE H S
Microbiology
55
Thara N K
Microbiology
56
POOJA J
Microbiology
57
SHASHIREKHA K S
Microbiology
58
Dr. Mangesh Kumar
Political Science
59
PAVITHRA M J
Political Science
60
PRAVEEN KUMAR N
Sanskrit (Language and Optional)
61
PRASHANTHA KUMARA S M
Zoology
62
ANITHA K A
Zoology
63
SYED MUZAHIR SHAH HUSSAINI
English (Language and Optional)
64
RUKMINI K S
Sociology
"""

def parse_guest_faculty(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    faculty = []
    
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            # Format is:
            # 1
            # ARCHANA
            # Biotechnology
            name = lines[i+1].strip()
            department_name = lines[i+2].strip()
            
            faculty.append({
                'name': name,
                'designation': 'Guest Faculty',
                'department': department_name
            })
            
    return faculty

app = create_app('development')

with app.app_context():
    print("Parsing guest faculty data...")
    faculty_data = parse_guest_faculty(guest_faculty_text)
    
    # Pre-create any missing departments
    departments = list(set([f['department'] for f in faculty_data]))
    for dept_name in departments:
        if not Department.query.filter_by(name=dept_name).first():
            new_dept = Department(name=dept_name)
            db.session.add(new_dept)
    db.session.commit()
    
    # Get department map
    dept_map = {d.name: d.id for d in Department.query.all()}
    
    added_count = 0
    for fac in faculty_data:
        # Create a simple username
        username = fac['name'].lower().replace('dr.', '').replace('prof.', '').replace(' ', '_').replace('.', '')
        # Clean up multiple underscores
        username = re.sub(r'_+', '_', username).strip('_')
        
        # Check if exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            # Update designation if needed
            if existing.designation != fac['designation']:
                existing.designation = fac['designation']
                existing.role = 'Faculty'
            continue
            
        dept_id = dept_map.get(fac['department'])
        
        user = User(
            username=username,
            email=f"{username}@gsc.edu.in",
            password_hash=generate_password_hash('Faculty@123'),
            full_name=fac['name'],
            role='Faculty',
            designation=fac['designation'],
            department_id=dept_id,
            is_active=True
        )
        db.session.add(user)
        added_count += 1
        print(f"  Added: {fac['name']} - {fac['designation']} in {fac['department']}")
        
    db.session.commit()
    print(f"\nAdded {added_count} new guest faculty members to the database.")
    print("Now the chatbot and tracking system will recognize them.")
