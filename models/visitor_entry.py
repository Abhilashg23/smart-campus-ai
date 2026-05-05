from models import db
from datetime import datetime


class VisitorEntry(db.Model):
    """Visitor entry/exit tracking with facial recognition"""
    __tablename__ = 'visitor_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    host_name = db.Column(db.String(150), nullable=True)  # Person/department being visited
    
    # Image storage
    photo = db.Column(db.LargeBinary, nullable=False)  # Visitor photo as BLOB
    face_encoding = db.Column(db.LargeBinary, nullable=True)  # Face recognition data
    
    # Entry/Exit tracking
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default='IN', nullable=False)  # 'IN' or 'OUT'
    
    # Returning visitor tracking
    is_returning_visitor = db.Column(db.Boolean, default=False)
    previous_visit_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_by_role = db.Column(db.String(50), default='kiosk')  # 'kiosk' or 'visitorentry'
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<VisitorEntry {self.name} - {self.status}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'reason': self.reason,
            'phone': self.phone,
            'organization': self.organization,
            'host_name': self.host_name,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'status': self.status,
            'is_returning_visitor': self.is_returning_visitor,
            'previous_visit_count': self.previous_visit_count,
            'created_by_role': self.created_by_role
        }
