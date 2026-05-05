from app import create_app
from models import db, User

app = create_app('development')

with app.app_context():
    # Fix Counselor
    counselor = User.query.filter_by(username='counciler').first()
    if not counselor:
        counselor = User.query.filter_by(email='counselor@smartcampus.edu').first()
    
    if counselor:
        counselor.username = 'counciler'
        print("Updated existing counselor user.")
    else:
        counselor = User(
            username='counciler',
            email='counselor@smartcampus.edu',
            full_name='Student Counselor',
            role='Counselor',
            is_approved=True,
            is_active=True
        )
        db.session.add(counselor)
        print("Created counselor user.")
    
    counselor.set_password('Welcome@1234')
    counselor.is_approved = True
    counselor.is_active = True
    counselor.role = 'Counselor'
    
    # Fix Security
    security = User.query.filter_by(username='Admin 2').first()
    if not security:
        security = User.query.filter_by(email='security@smartcampus.edu').first()
        
    if security:
        security.username = 'Admin 2'
        print("Updated existing security user.")
    else:
        security = User(
            username='Admin 2',
            email='security@smartcampus.edu',
            full_name='Security Admin',
            role='Security',
            is_approved=True,
            is_active=True
        )
        db.session.add(security)
        print("Created security user.")
        
    security.set_password('Welcome@1234')
    security.is_approved = True
    security.is_active = True
    security.role = 'Security'

    db.session.commit()
    print("Updated users successfully.")
