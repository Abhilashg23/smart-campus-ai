"""
Force reload face recognition service in running app
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.face_recognition import face_recognition_service

app = create_app('development')

def reload_faces():
    """Reload face recognition service"""
    with app.app_context():
        print("Reloading face recognition service...")
        print("-" * 60)
        
        # Clear existing faces
        face_recognition_service.known_faces = {}
        face_recognition_service._faces_loaded = False
        
        # Reload faces
        face_recognition_service.load_known_faces()
        
        print(f"\n✓ Loaded {len(face_recognition_service.known_faces)} faces")
        
        if face_recognition_service.known_faces:
            print("\nEnrolled users:")
            from models import User
            for user_id in face_recognition_service.known_faces.keys():
                user = User.query.get(user_id)
                if user:
                    print(f"  - {user.full_name} ({user.username})")
        
        print("\n" + "-" * 60)
        print("✓ Face recognition service reloaded!")


if __name__ == "__main__":
    reload_faces()
