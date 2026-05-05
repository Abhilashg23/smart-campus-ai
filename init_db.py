"""
Database initialization script for Smart Campus System
Creates all tables and seeds initial data
"""

from app import create_app
from models import db, User, Department
from services.chatbot import chatbot
import os


def init_database():
    """Initialize database with tables and seed data"""
    app = create_app('development')

    with app.app_context():
        # Drop all tables and recreate (for fresh start)
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        print("  Tables created successfully!")

        # Create departments from Government Science (Autonomous) Hassan
        departments_data = [
            {'name': 'B.Sc Physics', 'code': 'PHY', 'description': 'Bachelor of Science in Physics', 'head': 'Dr. NIRANJAN R S', 'contact_email': 'physics@gsc-hassan.edu.in', 'contact_phone': '08172-220001'},
            {'name': 'B.Sc Chemistry', 'code': 'CHM', 'description': 'Bachelor of Science in Chemistry', 'head': 'Dr. SHIVAPRASAD C M', 'contact_email': 'chemistry@gsc-hassan.edu.in', 'contact_phone': '08172-220002'},
            {'name': 'B.Sc Mathematics', 'code': 'MTH', 'description': 'Bachelor of Science in Mathematics', 'head': 'Dr. P.N. VINAY KUMAR', 'contact_email': 'maths@gsc-hassan.edu.in', 'contact_phone': '08172-220003'},
            {'name': 'B.Sc Computer Science', 'code': 'CSC', 'description': 'Bachelor of Science in Computer Science', 'head': 'Dr. Kousar', 'contact_email': 'cs@gsc-hassan.edu.in', 'contact_phone': '08172-220004'},
            {'name': 'B.Sc Botany', 'code': 'BOT', 'description': 'Bachelor of Science in Botany', 'head': 'Dr. Chandini KC', 'contact_email': 'botany@gsc-hassan.edu.in', 'contact_phone': '08172-220005'},
            {'name': 'B.Sc Zoology', 'code': 'ZOO', 'description': 'Bachelor of Science in Zoology', 'head': 'Dr. M. LATHA', 'contact_email': 'zoology@gsc-hassan.edu.in', 'contact_phone': '08172-220006'},
            {'name': 'B.Sc Biotechnology', 'code': 'BIO', 'description': 'Bachelor of Science in Biotechnology', 'head': 'Dr. SUDHEER ISHWAR MANAWADI', 'contact_email': 'biotech@gsc-hassan.edu.in', 'contact_phone': '08172-220007'},
            {'name': 'B.Sc Microbiology', 'code': 'MCB', 'description': 'Bachelor of Science in Microbiology', 'head': 'Dr. Raghavendra M P', 'contact_email': 'microbiology@gsc-hassan.edu.in', 'contact_phone': '08172-220010'},
            {'name': 'BCA', 'code': 'BCA', 'description': 'Bachelor of Computer Applications', 'head': 'Dept Head', 'contact_email': 'bca@gsc-hassan.edu.in', 'contact_phone': '08172-220011'},
            {'name': 'M.Sc Chemistry', 'code': 'MCH', 'description': 'Master of Science in Chemistry', 'head': 'PG Head', 'contact_email': 'mscchem@gsc-hassan.edu.in', 'contact_phone': '08172-220012'},
        ]

        for data in departments_data:
            dept = Department(
                name=data['name'],
                head_of_department=data['head'],
                contact_email=data['contact_email'],
                contact_phone=data['contact_phone']
            )
            db.session.add(dept)

        db.session.commit()
        print(f"  Created {len(departments_data)} departments")

        # Create admin user
        print("\nCreating admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            dept = Department.query.first()
            admin = User(
                username='admin',
                email='gsc_hassan@rediffmail.com',
                full_name='Dr. PRASANNA K S',
                role='Admin',
                is_approved=True,
                is_active=True,
                department_id=dept.id if dept else None
            )
            admin.set_password("Admin@GscHassan25")
            db.session.add(admin)
            db.session.commit()
            print("  Admin user created")
            print("  Username: admin")
            print("  Email: gsc_hassan@rediffmail.com")
            print("  Password: Admin@GscHassan25")

        # Create sample student
        print("\nCreating sample student...")
        cs_dept = Department.query.filter_by(name="B.Sc Computer Science").first() or Department.query.first()
        student = User(
            username="student1",
            email="student1@smartcampus.edu",
            full_name="John Doe",
            role="Student",
            department_id=cs_dept.id if cs_dept else None,
            is_approved=True,
            is_active=True
        )
        student.set_password("Student@123")

        db.session.add(student)
        db.session.commit()
        print("  Sample student created")
        print("  Username: student1")
        print("  Password: Student@123")

        # Create sample faculty
        print("\nCreating sample faculty...")
        faculty = User(
            username="faculty1",
            email="faculty1@smartcampus.edu",
            full_name="Dr. Jane Smith",
            role="Faculty",
            department_id=cs_dept.id if cs_dept else None,
            is_approved=True,
            is_active=True
        )
        faculty.set_password("Faculty@123")

        db.session.add(faculty)
        db.session.commit()
        print("  Sample faculty created")
        print("  Username: faculty1")
        print("  Password: Faculty@123")

        # Create security user
        print("\nCreating security user...")
        security = User(
            username="security",
            email="security@smartcampus.edu",
            full_name="Security Admin",
            role="Security",
            is_approved=True,
            is_active=True
        )
        security.set_password("Admin2")

        db.session.add(security)
        db.session.commit()
        print("  Security user created")
        print("  Username: security")
        print("  Password: Admin2")

        # Initialize chatbot
        print("\nInitializing AI chatbot...")
        api_key = os.environ.get('GOOGLE_API_KEY')
        if api_key:
            chatbot.initialize(api_key)
            print("  Chatbot initialized with Google API key")
        else:
            print("  Warning: GOOGLE_API_KEY not found in environment variables")
            print("  Chatbot will not work until you set the API key in .env file")

        print("\n" + "=" * 60)
        print("  Database initialization complete!")
        print("=" * 60)
        print("\nYou can now run the application with: python app.py")
        print("\nDefault login credentials:")
        print("  Admin    - username: admin,    password: Admin@GscHassan25")
        print("  Student  - username: student1, password: Student@123")
        print("  Faculty  - username: faculty1, password: Faculty@123")
        print("  Security - username: security, password: Admin2")
        print("\nDon't forget to:")
        print("  1. Add your GOOGLE_API_KEY to .env for chatbot features")
        print("  2. Update SECRET_KEY in .env for production")
        print("=" * 60)


if __name__ == '__main__':
    init_database()
