"""
Add recent Chanakya University events to the database
"""
from app import create_app
from models import db, Event
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Recent events from Chanakya University website
    events_data = [
        {
            'title': 'Strategic Reset: Ambassador Ashok K. Kantha Lecture',
            'description': 'Ambassador Ashok K. Kantha delivers insightful lecture on "Towards Neighbourhood First 2.0" and launches edited volume "Reconstructing India\'s Worldview: A Strategic Realignment". A comprehensive discussion on India\'s foreign policy and strategic positioning in the region.',
            'event_date': datetime(2026, 1, 11, 14, 0),  # January 11, 2026
            'location': 'Main Auditorium, Chanakya University'
        },
        {
            'title': 'Workshop on "Everyday Science: Where Curiosity Meets Reality"',
            'description': 'An engaging workshop designed for PUC students to explore the science behind everyday phenomena. Interactive sessions covering physics, chemistry, and biology concepts through practical demonstrations and hands-on experiments.',
            'event_date': datetime(2026, 1, 5, 10, 0),  # January 5, 2026
            'location': 'Science Lab Complex, Chanakya University'
        },
        {
            'title': 'Roundtable on Concept and Predicate Commonality Across Indian Languages',
            'description': 'An academic roundtable discussion exploring linguistic patterns and commonalities across various Indian languages. Featuring renowned linguists and scholars discussing the philosophical and practical aspects of language structure.',
            'event_date': datetime(2026, 1, 5, 15, 0),  # January 5, 2026
            'location': 'Conference Room A, Chanakya University'
        },
        {
            'title': '10th Sammilan - A Celebration of Community and Excellence',
            'description': 'The 10th edition of Sammilan, Chanakya University\'s flagship community celebration event. A day filled with cultural performances, academic achievements recognition, sports competitions, and community bonding activities.',
            'event_date': datetime(2026, 1, 4, 9, 0),  # January 4, 2026
            'location': 'University Grounds, Chanakya University'
        }
    ]
    
    print("Adding Chanakya University events to database...")
    
    # Get admin user for created_by field
    from models import User
    admin_user = User.query.filter_by(role='Admin').first()
    
    if not admin_user:
        print("Error: No admin user found. Please create an admin user first.")
        exit(1)
    
    for event_data in events_data:
        # Check if event already exists
        existing_event = Event.query.filter_by(title=event_data['title']).first()
        
        if existing_event:
            print(f"Event already exists: {event_data['title']}")
            continue
        
        # Add created_by field
        event_data['created_by'] = admin_user.id
        
        # Create new event
        event = Event(**event_data)
        db.session.add(event)
        print(f"Added event: {event_data['title']}")
    
    db.session.commit()
    print("\n✅ Successfully added all Chanakya University events!")
    print(f"Total events in database: {Event.query.count()}")
