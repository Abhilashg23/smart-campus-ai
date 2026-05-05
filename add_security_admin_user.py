#!/usr/bin/env python3
"""
Add Security Admin user to the database
Username: securityadmin
Password: Welcome@1234
Role: SecurityAdmin - Can view both student/faculty tracking AND visitor entry/exit
"""

from app import create_app
from models import db, User

def add_security_admin_user():
    """Add the security admin user"""
    app = create_app('development')
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='securityadmin').first()
        
        if existing_user:
            print("✓ Security Admin user already exists")
            print(f"  Username: {existing_user.username}")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role}")
            return
        
        # Create new security admin user
        security_admin = User(
            username='securityadmin',
            email='securityadmin@smartcampus.edu',
            full_name='Security Admin',
            role='SecurityAdmin',
            is_approved=True,
            is_active=True
        )
        security_admin.set_password('Welcome@1234')
        
        db.session.add(security_admin)
        db.session.commit()
        
        print("✓ Security Admin user created successfully!")
        print(f"  Username: securityadmin")
        print(f"  Password: Welcome@1234")
        print(f"  Role: SecurityAdmin")
        print(f"  Email: securityadmin@smartcampus.edu")
        print(f"\n  This user can access:")
        print(f"    - Student/Faculty tracking (like Security role)")
        print(f"    - Visitor entry/exit management (like VisitorEntry role)")

if __name__ == '__main__':
    add_security_admin_user()
