from app import create_app
from models import db
from models.emotion_tracking import EmotionTracking

app = create_app('development')


def create_table():
    with app.app_context():
        # Create table
        db.create_all()
        print("EmotionTracking table created successfully!")

if __name__ == "__main__":
    create_table()
