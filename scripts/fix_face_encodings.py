"""
Fix existing face encodings - convert from tobytes to pickle format
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, FaceData
import numpy as np
import pickle

app = create_app('development')

def fix_face_encodings():
    """Convert existing face encodings from tobytes to pickle format"""
    with app.app_context():
        print("Fixing face encodings...")
        print("-" * 60)
        
        # Get all face data records
        face_records = FaceData.query.all()
        print(f"\nFound {len(face_records)} face encoding records")
        
        fixed_count = 0
        error_count = 0
        
        for record in face_records:
            try:
                # Try to load as pickle first (already fixed)
                try:
                    encoding = pickle.loads(record.face_encoding)
                    print(f"✓ User {record.user_id}: Already in pickle format")
                    continue
                except:
                    pass
                
                # Convert from tobytes format
                print(f"\n  Converting User {record.user_id}...")
                
                # Load from tobytes format
                encoding = np.frombuffer(record.face_encoding, dtype=np.float64)
                print(f"    - Loaded encoding: shape {encoding.shape}")
                
                # Save in pickle format
                record.face_encoding = pickle.dumps(encoding)
                fixed_count += 1
                print(f"    - ✓ Converted to pickle format")
                
            except Exception as e:
                print(f"    - ✗ Error: {str(e)}")
                error_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\n✓ Fixed {fixed_count} face encodings")
        
        if error_count > 0:
            print(f"✗ Failed to fix {error_count} encodings")
        
        # Test loading
        print("\n" + "-" * 60)
        print("Testing face recognition service...")
        from services.face_recognition import face_recognition_service
        face_recognition_service.load_known_faces()
        print(f"✓ Loaded {len(face_recognition_service.known_faces)} faces successfully!")
        
        print("\n" + "-" * 60)
        print("✓ Migration complete!")


if __name__ == "__main__":
    fix_face_encodings()
