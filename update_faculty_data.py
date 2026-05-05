import os
from app import create_app
from models import db, User

data = [
    ("Geetha C D", "PHP, R Programming", "A Block"),
    ("Madhura Yadav MP", "Python, PHP", "A Block"),
    ("Manjunath D", "CN, Software Engineering", "B Block"),
    ("Darshan S J", "FDS, Software Engineering", "B Block"),
    ("Smitha R P", "CN, Cyber Security", "A Block"),
    ("Ravi N C", "Kannada", "B Block"),
    ("Chethana", "English", "B Block"),
    ("Sajeeth Kumar Pujar", "DS, Java", "A Block"),
    ("Manjunatha Guru V G", "AI, R Programming", "A Block"),
    ("Mamatha C", "Python, AI", "A Block"),
    ("Chudamani", "EVS", "B Block")
]

app = create_app()
with app.app_context():
    for name, subjects, cabin in data:
        # Search for faculty
        user = User.query.filter(User.full_name.ilike(f"%{name}%")).first()
        if user:
            user.specialization = subjects
            user.bio = f"Cabin Location: {cabin}"
            print(f"Updated {name}")
        else:
            print(f"User {name} not found!")
    
    db.session.commit()
    print("Database update complete!")
