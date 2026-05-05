"""
Update Sri Naresh Dixit P. S. faculty profile with detailed information
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User

app = create_app('development')

def update_naresh_dixit_profile():
    """Update Sri Naresh Dixit P. S. profile"""
    with app.app_context():
        print("Updating Sri Naresh Dixit P. S. profile...")
        
        # Find the user
        user = User.query.filter(User.full_name.like('%Naresh Dixit%')).first()
        
        if not user:
            print("User not found!")
            return
        
        print(f"Found user: {user.full_name}")
        
        # Update profile information
        user.designation = "Assistant Professor and Convener, Institutions Innovation Council"
        user.education = "M.Tech., VTU, Belagavi"
        user.bio = "Former Research Associate, Indian Institute of Science, Bengaluru"
        
        # Note: Profile image needs to be manually saved to static/images/faculty/engineering/
        # The image path will be: /static/images/faculty/engineering/sri_naresh_dixit_ps.jpg
        
        db.session.commit()
        
        print("\n✓ Profile updated successfully!")
        print(f"Name: {user.full_name}")
        print(f"Designation: {user.designation}")
        print(f"Education: {user.education}")
        print(f"Bio: {user.bio}")
        print(f"Email: {user.email}")


if __name__ == "__main__":
    update_naresh_dixit_profile()
