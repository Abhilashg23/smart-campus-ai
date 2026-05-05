from app import create_app
from models import db, User

app = create_app('development')

def create_counselor():
    with app.app_context():
        # Check if counselor already exists
        user = User.query.filter_by(username='counciler').first()
        
        if user:
            print("Counselor user already exists!")
            return
        
        # Create counselor user
        counselor = User(
            username='counciler',
            email='counselor@smartcampus.edu',
            full_name='Student Counselor',
            role='Counselor',
            is_approved=True,
            is_active=True
        )
        
        counselor.set_password('Welcome@1234')
        db.session.add(counselor)
        db.session.commit()
        
        print("Counselor user created successfully!")
        print("Username: counciler")
        print("Password: Welcome@1234")

if __name__ == "__main__":
    create_counselor()
