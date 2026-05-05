"""
Reset all faculty passwords to default password: Welcome@1234
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User

app = create_app('development')

def reset_faculty_passwords():
    """Reset all faculty passwords to Welcome@1234"""
    with app.app_context():
        print("Resetting faculty passwords...")
        
        # Get all faculty users
        faculty_users = User.query.filter_by(role='Faculty').all()
        
        if not faculty_users:
            print("No faculty users found.")
            return
        
        default_password = "Welcome@1234"
        updated_count = 0
        
        print(f"\nFound {len(faculty_users)} faculty members:")
        print("-" * 80)
        
        for faculty in faculty_users:
            # Set the new password
            faculty.set_password(default_password)
            updated_count += 1
            
            # Display info
            username = faculty.username or "N/A"
            email = faculty.email or "N/A"
            full_name = faculty.full_name or "N/A"
            
            print(f"✓ {full_name:30} | Username: {username:25} | Email: {email}")
        
        # Commit all changes
        db.session.commit()
        
        print("-" * 80)
        print(f"\n✓ Successfully reset passwords for {updated_count} faculty members")
        print(f"  Default Password: {default_password}")
        print(f"\nAll faculty can now login with:")
        print(f"  Username: [their username]")
        print(f"  Password: {default_password}")
        print("\nNote: Faculty should change their password after first login.")


if __name__ == "__main__":
    reset_faculty_passwords()
