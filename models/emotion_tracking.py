from models import db
from datetime import datetime
import json

class EmotionTracking(db.Model):
    """Emotion tracking model linked to entry/exit events"""
    __tablename__ = 'emotion_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tracking_id = db.Column(db.Integer, db.ForeignKey('student_tracking.id'), nullable=True)
    
    # Emotion data
    dominant_emotion = db.Column(db.String(20), nullable=False)
    emotion_scores = db.Column(db.Text)  # JSON string of all emotion scores
    confidence = db.Column(db.Float)
    
    # Demographics from Face Analysis
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='emotion_records')
    tracking_record = db.relationship('StudentTracking', backref='emotion_data')
    
    def set_emotion_scores(self, scores_dict):
        """Save emotion scores as JSON"""
        self.emotion_scores = json.dumps(scores_dict)
        
    def get_emotion_scores(self):
        """Get emotion scores as dict"""
        if self.emotion_scores:
            return json.loads(self.emotion_scores)
        return {}
        
    def __repr__(self):
        return f'<EmotionTracking {self.user_id} - {self.dominant_emotion} at {self.timestamp}>'
