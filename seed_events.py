import os
from datetime import datetime, timedelta
from app import create_app
from models import db, Event, User

app = create_app()

def seed_events():
    with app.app_context():
        # Find an admin user to be the creator
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("No admin user found. Creating a temporary admin user...")
            admin_user = User(
                username='event_admin',
                email='event_admin@example.com',
                full_name='System Admin',
                role='admin'
            )
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()

        # Check if events already exist
        if Event.query.count() > 0:
            print("Events already exist in the database. Cleaning up old events...")
            Event.query.delete()
            db.session.commit()

        # Create dummy events
        now = datetime.utcnow()
        dummy_events = [
            Event(
                title="Annual Cultural Fest - 'Spandana'",
                description="Join us for the biggest cultural extravaganza of the year. Featuring music, dance, theater, and art exhibitions from our talented students.",
                event_date=now + timedelta(days=5, hours=10),
                location="Main Auditorium",
                created_by=admin_user.id
            ),
            Event(
                title="Tech Symposium 2026",
                description="A two-day technology symposium featuring guest speakers from top tech companies, student project showcases, and coding competitions.",
                event_date=now + timedelta(days=12, hours=4),
                location="BCA Block, Seminar Hall",
                created_by=admin_user.id
            ),
            Event(
                title="Inter-Department Sports Meet",
                description="Annual sports competition between all departments. Track and field events, basketball, volleyball, and more.",
                event_date=now + timedelta(days=20, hours=2),
                location="College Sports Arena",
                created_by=admin_user.id
            ),
            Event(
                title="Career Fair & Alumni Connect",
                description="Meet successful alumni and top recruiters. Bring your resumes! Open to all final year students.",
                event_date=now + timedelta(days=25, hours=6),
                location="Main Block Quadrangle",
                created_by=admin_user.id
            ),
            Event(
                title="Science Exhibition",
                description="Showcase of innovative science projects by our undergraduate and postgraduate students. Open to public.",
                event_date=now + timedelta(days=35, hours=5),
                location="Science Block Labs",
                created_by=admin_user.id
            )
        ]

        for event in dummy_events:
            db.session.add(event)
        
        db.session.commit()
        print(f"Successfully added {len(dummy_events)} upcoming dummy events!")

if __name__ == '__main__':
    seed_events()
