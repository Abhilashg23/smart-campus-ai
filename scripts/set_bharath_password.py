"""
Set password for bharath_setturu user
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User

app = create_app('development')

def set_bharath_password():
    """Set password for bharath_setturu to Welcome@1234"""
    with app.app_context():
        print("Setting password for bharath_setturu...")
        
        # Find user
        user = User.query.filter_by(username='bharath_setturu').first()
        
        if not user:
            print("❌ User 'bharath_setturu' not found in database")
            print("\nSearching for similar usernames...")
            similar = User.query.filter(User.username.like('%bharath%')).all()
            if similar:
                print("Found similar users:")
                for u in similar:
                    print(f"  - {u.username} ({u.full_name})")
            return
        
        # Set password
        default_password = "Welcome@1234"
        user.set_password(default_password)
        db.session.commit()
        
        print(f"\n✓ Password set successfully!")
        print(f"  Username: {user.username}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Password: {default_password}")
        print(f"\nUser can now login with:")
        print(f"  Username: {user.username}")
        print(f"  Password: {default_password}")


if __name__ == "__main__":
    set_bharath_password()
