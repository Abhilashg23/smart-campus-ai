from models import db
from datetime import datetime


class AnonymousMessage(db.Model):
    """Anonymous message/complaint model"""
    __tablename__ = 'anonymous_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # complaint, suggestion, feedback, other
    sender_role = db.Column(db.String(20), nullable=True)  # Optional role tracking
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved
    is_read = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<AnonymousMessage {self.id} ({self.category})>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category,
            'message': self.message,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'is_read': self.is_read,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sender_role': self.sender_role
        }
