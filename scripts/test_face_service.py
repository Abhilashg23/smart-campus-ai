"""
Test and reload face recognition service
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.face_recognition import face_recognition_service

app = create_app('development')

def test_face_service():
    """Test face recognition service"""
    with app.app_context():
        print("Testing Face Recognition Service...")
        print("-" * 60)
        
        # Load faces
        print("\n1. Loading known faces...")
        face_recognition_service.load_known_faces()
        
        # Check loaded faces
        print(f"\n2. Loaded faces count: {len(face_recognition_service.known_faces)}")
        
        if face_recognition_service.known_faces:
            print("\n3. Enrolled users:")
            for user_id, encoding in face_recognition_service.known_faces.items():
                from models import User
                user = User.query.get(user_id)
                if user:
                    print(f"   - User ID {user_id}: {user.full_name} ({user.username})")
                    print(f"     Encoding shape: {encoding.shape if hasattr(encoding, 'shape') else 'N/A'}")
        else:
            print("\n3. ❌ No faces loaded!")
            print("   Checking database...")
            from models import FaceData
            face_count = FaceData.query.count()
            print(f"   Face data records in database: {face_count}")
        
        print("\n" + "-" * 60)
        print("✓ Test complete!")


if __name__ == "__main__":
    test_face_service()
