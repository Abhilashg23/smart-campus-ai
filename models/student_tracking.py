from models import db
from datetime import datetime


class StudentTracking(db.Model):
    """Student entry/exit tracking model"""
    __tablename__ = 'student_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_type = db.Column(db.String(10), nullable=False)  # 'IN' or 'OUT'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verification_method = db.Column(db.String(20), default='face')  # face recognition
    location = db.Column(db.String(100), default='Main Gate')
    
    # Relationship
    user = db.relationship('User', backref='tracking_records')
    
    def __repr__(self):
        return f'<StudentTracking {self.user_id} - {self.entry_type} at {self.timestamp}>'
