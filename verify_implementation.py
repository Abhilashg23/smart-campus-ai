from app import create_app
from models import db, User, EmotionTracking

app = create_app('development')

def verify():
    with app.app_context():
        print("Verifying implementation...")
        
        # 1. Check Counselor User
        counselor = User.query.filter_by(username='counciler').first()
        if counselor:
            print(f"✅ Counselor user found: {counselor.username} (Role: {counselor.role})")
        else:
            print("❌ Counselor user NOT found!")
            
        # 2. Check EmotionTracking Table
        try:
            # Create a dummy record (rollback later)
            count = EmotionTracking.query.count()
            print(f"✅ EmotionTracking table exists. Current record count: {count}")
        except Exception as e:
            print(f"❌ Error checking EmotionTracking table: {e}")
            
        print("Verification complete.")

if __name__ == "__main__":
    verify()
