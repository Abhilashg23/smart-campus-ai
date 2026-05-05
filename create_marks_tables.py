from app import create_app
from models import db, SystemConfig, Subject, InternalMarks, SubjectFeedback, User, Program

app = create_app('development')

with app.app_context():
    print("Creating new tables for marks and feedback...")
    db.create_all()
    print("Tables created.")
    
    # Check if there are any subjects, if not, create some mock ones
    if Subject.query.count() == 0:
        print("Creating mock subjects...")
        program = Program.query.first()
        faculty = User.query.filter_by(role='Faculty').first()
        
        if program and faculty:
            # Create some dummy subjects for testing
            s1 = Subject(name='Data Structures', code='CS201', program_id=program.id, semester=3, faculty_id=faculty.id)
            s2 = Subject(name='Algorithms', code='CS202', program_id=program.id, semester=3, faculty_id=faculty.id)
            s3 = Subject(name='Database Systems', code='CS301', program_id=program.id, semester=4, faculty_id=faculty.id)
            db.session.add_all([s1, s2, s3])
            db.session.commit()
            print("Mock subjects created.")
        else:
            print("Could not create mock subjects: No program or faculty found.")
