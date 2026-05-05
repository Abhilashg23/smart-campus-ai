from app import create_app
from models import db, Subject, User, Department, Program

app = create_app('development')

with app.app_context():
    print("Seeding subjects and programs...")
    
    # 1. Ensure we have a faculty
    faculty = User.query.filter_by(role='Faculty').first()
    if not faculty:
        print("No faculty found. Please run init_db.py first.")
        exit(1)
        
    # 2. Get the department for B.Sc Computer Science
    dept = Department.query.filter(Department.name.like('%Computer%')).first()
    if not dept:
        dept = Department.query.first()
        
    # 3. Create a Program
    program = Program.query.filter_by(code='BCA-01').first()
    if not program:
        program = Program(name='Bachelor of Computer Applications', code='BCA-01', department_id=dept.id, duration_years=3)
        db.session.add(program)
        db.session.commit()
        print("Created Program:", program.name)
        
    # 4. Create Subjects
    if Subject.query.count() == 0:
        s1 = Subject(name='Data Structures using C', code='BCA301', program_id=program.id, semester=3, faculty_id=faculty.id)
        s2 = Subject(name='Object Oriented Programming with C++', code='BCA302', program_id=program.id, semester=3, faculty_id=faculty.id)
        s3 = Subject(name='Database Management Systems', code='BCA303', program_id=program.id, semester=3, faculty_id=faculty.id)
        db.session.add_all([s1, s2, s3])
        db.session.commit()
        print("Mock subjects created and assigned to faculty:", faculty.full_name)
    else:
        print("Subjects already exist.")
        
    # Ensure student belongs to this program and semester
    student = User.query.filter_by(username='student1').first()
    if student:
        student.program_id = program.id
        student.semester = 3
        db.session.commit()
        print("Updated student1 program and semester.")
