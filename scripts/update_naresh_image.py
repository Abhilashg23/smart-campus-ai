"""
Update Sri Naresh Dixit P. S. profile image path
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User

app = create_app('development')

def update_profile_image():
    """Update profile image path"""
    with app.app_context():
        print("Updating profile image path...")
        
        # Find the user
        user = User.query.filter(User.full_name.like('%Naresh Dixit%')).first()
        
        if not user:
            print("User not found!")
            return
        
        # Update profile image path
        user.profile_image = "/static/images/faculty/engineering/sri_naresh_dixit_ps.jpg"
        
        db.session.commit()
        
        print(f"\n✓ Profile image updated!")
        print(f"Image path: {user.profile_image}")


if __name__ == "__main__":
    update_profile_image()
