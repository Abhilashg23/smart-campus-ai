"""
Attention Log Model
Stores classroom attention monitoring data
"""

from models import db
from datetime import datetime


class AttentionLog(db.Model):
    """Model for storing attention monitoring session data"""
    
    __tablename__ = 'attention_log'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Faculty who is monitoring (nullable to avoid foreign key issues during migration)
    faculty_id = db.Column(db.Integer, nullable=True)
    
    # Session identifier (to group continuous monitoring)
    session_id = db.Column(db.String(50), nullable=False, index=True)
    
    # Attention metrics
    total_students = db.Column(db.Integer, default=0)
    focused_count = db.Column(db.Integer, default=0)
    distracted_count = db.Column(db.Integer, default=0)
    
    # Alert flag
    alert_triggered = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AttentionLog {self.id} - {self.timestamp} - {self.focused_count}/{self.total_students} focused>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'faculty_id': self.faculty_id,
            'session_id': self.session_id,
            'total_students': self.total_students,
            'focused_count': self.focused_count,
            'distracted_count': self.distracted_count,
            'alert_triggered': self.alert_triggered
        }
