"""
Add security user to the database
Username: Admin 2
Password: Admin@Chanakya25
Role: Security
"""

from app import create_app
from models import db, User

def add_security_user():
    """Add security user to database"""
    app = create_app('development')
    
    with app.app_context():
        # Check if security user already exists
        existing_user = User.query.filter_by(username='Admin 2').first()
        
        if existing_user:
            print("Security user 'Admin 2' already exists!")
            print(f"User ID: {existing_user.id}")
            print(f"Role: {existing_user.role}")
            print(f"Approved: {existing_user.is_approved}")
            print(f"Active: {existing_user.is_active}")
            return
        
        # Create security user
        security_user = User(
            username='Admin 2',
            email='security@smartcampus.edu',
            full_name='Security Admin',
            role='Security',
            is_approved=True,
            is_active=True
        )
        
        # Set password
        security_user.set_password('Admin@Chanakya25')
        
        # Add to database
        db.session.add(security_user)
        db.session.commit()
        
        print("✓ Security user created successfully!")
        print(f"Username: Admin 2")
        print(f"Password: Admin@Chanakya25")
        print(f"Role: Security")
        print(f"User ID: {security_user.id}")
        print(f"\nYou can now login at: http://localhost:5001/security/login")


if __name__ == '__main__':
    add_security_user()
