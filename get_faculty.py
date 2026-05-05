from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    faculty = User.query.filter_by(role='faculty').all()
    print("Faculty in DB:")
    for f in faculty:
        dept = f.department.name if f.department else "No Dept"
        print(f"- {f.full_name} ({dept})")
