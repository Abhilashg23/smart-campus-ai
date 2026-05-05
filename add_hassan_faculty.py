"""
Script to add Hassan Science College faculty data to database
"""
import re
from app import create_app
from models import db, User, Department
from werkzeug.security import generate_password_hash

faculty_text = """
#### 1
#### Dr. PRASANNA K S
#### Principal(Associate Professor in Zoology)
#### 2
#### Dr. Sundaresha  S
#### Professor in Kannada
#### 3
#### Dr. Ravi N C
#### Associate  Professor in Kannada
#### 4
#### Dr. POORNIMA K B
#### Associate Professor in English
#### 5
#### Dr. Chandini KC
#### Associate Professor in Botany
#### 6
#### SHARU RAJ K M
#### Associate Professor in Botany
#### 7
#### Dr.Dharmendra
#### Associate Professor in Botany
#### 8
#### Dr. SANDHYA RANI D
#### Associate Professor in Botany
#### 9
#### Dr. Suresha   N S
#### Associate Professor in Botany
#### 10
#### KAVITHA K R
#### Assistant Professor in Biochemistry
#### 11
#### SUNITHA
#### Assistant Professor in Biochemistry
#### 12
#### BHARGAVA C S
#### Assistant Professor in Biochemistry
#### 13
#### UMME NAJMA
#### Assistant Professor in Biotechnology
#### 14
#### Dr. SUDHEER ISHWAR MANAWADI
#### Assistant Professor in Biotechnology
#### 15
#### Dr. SANJOTHA G
#### Assistant Professor in Biotechnology
#### 16
#### LATA KULAKARNI
#### Assistant Professor in Electronics
#### 17
#### Dr.Thalari Chandrasekhar
#### Associate Professor in Electronics
#### 18
#### Divyamani   M P
#### Assistant Professor in Electronics
#### 19
#### Ramayya Nayak K
#### Associate Professor in Chemistry
#### 20
#### TARA M K
#### Associate Professor in Chemistry
#### 21
#### Dr. SHIVAPRASAD C M
#### Professor in Chemistry
#### 22
#### Dr. Mohan Kumar B V
#### Associate Professor in Chemistry
#### 23
#### Dr. KAVITHA C N
#### Professor in Chemistry
#### 24
#### Dr. GIRIDHAR M
#### Assistant Professor in Chemistry
#### 25
#### Dr. NIRANJAN R S
#### Associate Professor in Physics
#### 26
#### KRISHNA MOHAN R
#### Assistant Professor in Physics
#### 27
#### Dr. Raghu  A
#### Associate Professor in Physics
#### 28
#### Dr. Rajeeva  M P
#### Assistant Professor in Physics
#### 29
#### KAVITHA B S
#### Assistant Professor in Physics
#### 30
#### PRASANNA KUMARA S G
#### Assistant Professor in Physics
#### 31
#### SHIVAKUMAR B S
#### Assistant Professor in Physics
#### 32
#### JAGADEESH S S
#### Assistant Professor in Physics
#### 33
#### Dr.P.N.VINAY KUMAR
#### Professor in Mathematics
#### 34
#### Dr. Vijay S
#### Associate Professor in Mathematics
#### 35
#### DARSHAN A
#### Assistant Professor in Mathematics
#### 36
#### Dr. SUDHAKARA K. B.
#### Associate Professor in Mathematics
#### 37
#### Dr. Harshavardhan   C N
#### Associate Professor in Mathematics
#### 38
#### JYOTHIKIRAN S
#### Assistant Professor in Mathematics
#### 39
#### Dr. ANITHA V
#### Assistant Professor in Mathematics
#### 40
#### Dr. Raghavendra   M P
#### Professor in Microbiology
#### 41
#### Dr. M. LATHA
#### Associate Professor in Zoology
#### 42
#### Dr. SHIVAKUMAR P
#### Associate Professor in Zoology
#### 43
#### Dr. SUCHITRA  G
#### Associate Professor in Zoology
#### 44
#### Annapurneshwari H
#### Assistant Professor in Zoology
#### 45
#### Dr. HEMESHA H.N.
#### Selection Grade Librarian
#### 46
#### MYTHRI C.D
#### Director of Physical Education
#### 47
#### KRISHNAMOORTHY VAIDYA
#### Director of Physical Education
#### 48
#### Dr. Kousar
#### Assistant Professor in Computer Science
#### 49
#### Madhura Yadav  M P
#### Assistant Professor in Computer Science
#### 50
#### Geetha  C D
#### Assistant Professor in Computer Science
#### 51
#### Sheela  N S
#### Assistant Professor in Computer Science
#### 52
#### Manjunatha  Guru  V G
#### Assistant Professor in Computer Science
#### 53
#### Sajeetkumar Pujar
#### Assistant Professor in Computer Science
#### 54
#### Dr. Shwetha  M
#### Assistant Professor in Physics
#### 55
#### UDAYADITHYA  M V
#### Assistant Professor in BioChemistry
#### 56
#### THILAGAVATHY  A
#### Assistant Professor in BioChemistry
#### 57
#### RAMITHA  B  R
#### Assistant Professor in Chemistry
#### 58
#### PALLAVI
#### Assistant Professor in Chemistry
#### 59
#### SANTOSH  KUMAR  S C
#### Assistant Professor in Chemistry
#### 60
#### RANJITH C GOWDA
#### Assistant Professor in Chemistry
#### 61
#### DEZIY MELITA  D SOUZA
#### Assistant Professor in Chemistry
#### 62
#### KIRAN KUMAR  H
#### Assistant Professor in Chemistry
"""

def parse_faculty(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    faculty = []
    
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            # Format is:
            # #### 1
            # #### Dr. Name
            # #### Designation
            name = lines[i+1].replace('#### ', '').strip()
            designation = lines[i+2].replace('#### ', '').strip()
            
            # Extract department from designation
            # Example: Assistant Professor in Biochemistry -> Biochemistry
            department_name = "General"
            match = re.search(r'in\s+([A-Za-z\s]+)', designation)
            if match:
                department_name = match.group(1).strip()
                
            faculty.append({
                'name': name,
                'designation': designation,
                'department': department_name
            })
            
    return faculty

app = create_app('development')

with app.app_context():
    print("Parsing faculty data...")
    faculty_data = parse_faculty(faculty_text)
    
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
            # Maybe update designation if it changed
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
        print(f"  Added: {fac['name']} - {fac['designation']}")
        
    db.session.commit()
    print(f"\nAdded {added_count} new faculty members to the database.")
    print("Now the chatbot and tracking system will recognize them.")
