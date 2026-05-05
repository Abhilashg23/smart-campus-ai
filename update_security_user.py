"""
Update security user credentials
Changes username from 'Admin 2' to 'security' and password to 'Admin2'
"""

from app import create_app
from models import db, User

def update_security_user():
    """Update security user credentials"""
    app = create_app('development')
    
    with app.app_context():
        # Find the existing security user
        old_user = User.query.filter_by(username='Admin 2', role='Security').first()
        
        if old_user:
            print(f"Found existing security user: {old_user.username}")
            print("Updating username to: security")
            print("Updating password to: Admin2")
            
            old_user.username = 'security'
            old_user.set_password('Admin2')
            old_user.is_approved = True
            old_user.is_active = True
            
            db.session.commit()
            print("✓ Security user updated successfully!")
        else:
            # Check if 'security' user already exists
            security_user = User.query.filter_by(username='security').first()
            
            if security_user:
                print(f"User 'security' already exists!")
                print(f"Role: {security_user.role}")
                print("Updating password to: Admin2")
                security_user.set_password('Admin2')
                security_user.is_approved = True
                security_user.is_active = True
                db.session.commit()
                print("✓ Password updated successfully!")
            else:
                # Create new security user
                print("Creating new security user...")
                security_user = User(
                    username='security',
                    email='security@smartcampus.edu',
                    full_name='Security Admin',
                    role='Security',
                    is_approved=True,
                    is_active=True
                )
                security_user.set_password('Admin2')
                
                db.session.add(security_user)
                db.session.commit()
                print("✓ Security user created successfully!")
        
        print("\n" + "="*50)
        print("Security Login Credentials:")
        print("="*50)
        print("  Username: security")
        print("  Password: Admin2")
        print("  Login URL: http://127.0.0.1:5001/auth/login")
        print("="*50)

if __name__ == '__main__':
    update_security_user()
