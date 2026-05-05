#!/usr/bin/env python3
"""
Add Visitor Entry user to the database
Username: visitorentry
Password: Welcome@1234
"""

from app import create_app
from models import db, User

def add_visitor_entry_user():
    """Add the visitor entry user"""
    app = create_app('development')
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='visitorentry').first()
        
        if existing_user:
            print("✓ Visitor Entry user already exists")
            print(f"  Username: {existing_user.username}")
            print(f"  Email: {existing_user.email}")
            print(f"  Role: {existing_user.role}")
            return
        
        # Create new visitor entry user
        visitor_user = User(
            username='visitorentry',
            email='visitorentry@smartcampus.edu',
            full_name='Visitor Entry Manager',
            role='VisitorEntry',
            is_approved=True,
            is_active=True
        )
        visitor_user.set_password('Welcome@1234')
        
        db.session.add(visitor_user)
        db.session.commit()
        
        print("✓ Visitor Entry user created successfully!")
        print(f"  Username: visitorentry")
        print(f"  Password: Welcome@1234")
        print(f"  Role: VisitorEntry")
        print(f"  Email: visitorentry@smartcampus.edu")

if __name__ == '__main__':
    add_visitor_entry_user()
