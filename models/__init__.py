from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

# Import StudentTracking model
from models.student_tracking import StudentTracking


# Import AnonymousMessage model
from models.anonymous_message import AnonymousMessage

# Import EmotionTracking model
from models.emotion_tracking import EmotionTracking

# Import AttentionLog model
from models.attention_log import AttentionLog

# Import VisitorEntry model
from models.visitor_entry import VisitorEntry


class User(UserMixin, db.Model):
    """User model with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Student, Faculty, Common
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Faculty-specific fields
    profile_image = db.Column(db.String(500), nullable=True)  # Faculty profile image path
    designation = db.Column(db.String(200), nullable=True)  # e.g., "Associate Professor"
    specialization = db.Column(db.Text, nullable=True)  # Area of expertise
    education = db.Column(db.Text, nullable=True)  # Educational qualifications
    bio = db.Column(db.Text, nullable=True)  # About/biography
    research_interests = db.Column(db.Text, nullable=True)  # Research areas
    publications = db.Column(db.Text, nullable=True)  # Key publications
    university_profile_url = db.Column(db.String(500), nullable=True)  # Link to university profile
    
    # Student-specific fields
    first_name = db.Column(db.String(100), nullable=True)  # Student first name
    last_name = db.Column(db.String(100), nullable=True)  # Student last name
    registration_id = db.Column(db.String(50), unique=True, nullable=True, index=True)  # Student registration/roll number
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=True)  # Academic program
    year = db.Column(db.Integer, nullable=True)  # Academic year (1, 2, 3, 4)
    semester = db.Column(db.Integer, nullable=True)  # Semester (1-8)
    section = db.Column(db.String(10), nullable=True)  # Section (A, B, C, etc.)
    
    # Relationships
    department = db.relationship('Department', backref='users')
    program = db.relationship('Program', backref='students')
    attendance_records = db.relationship('Attendance', backref='user', lazy='dynamic')
    chat_history = db.relationship('ChatHistory', backref='user', lazy='dynamic')
    face_data = db.relationship('FaceData', backref='user', lazy='dynamic')
    created_events = db.relationship('Event', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'Admin'
    
    def is_student(self):
        """Check if user is student"""
        return self.role == 'Student'
    
    def is_faculty(self):
        """Check if user is faculty"""
        return self.role == 'Faculty'
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    head_of_department = db.Column(db.String(150))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    programs = db.relationship('Program', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'


class Program(db.Model):
    """Academic Program model (e.g., B.Tech CSE, B.Tech ECE)"""
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "B.Tech Computer Science"
    code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "BTECH-CSE"
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    duration_years = db.Column(db.Integer, default=4)  # Program duration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Program {self.name}>'


class Event(db.Model):
    """Event model for campus events"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='events')
    
    def __repr__(self):
        return f'<Event {self.title}>'


class Attendance(db.Model):
    """Attendance tracking model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='present')  # present, absent
    verification_method = db.Column(db.String(20), default='manual')  # face, manual
    location = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Attendance {self.user_id} at {self.timestamp}>'


class ChatHistory(db.Model):
    """Chat history storage"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    chat_type = db.Column(db.String(20), default='text')  # text, voice
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatHistory {self.user_id} at {self.timestamp}>'


class FaceData(db.Model):
    """Face recognition data storage"""
    __tablename__ = 'face_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)  # Stored as binary
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FaceData for user {self.user_id}>'


class PendingRegistration(db.Model):
    """Pending user registrations awaiting admin approval"""
    __tablename__ = 'pending_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    qr_token = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def __repr__(self):
        return f'<PendingRegistration {self.username} ({self.status})>'


class SystemConfig(db.Model):
    """Global configuration settings"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_value(cls, key, default=None):
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
        
    @classmethod
    def set_value(cls, key, value):
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
        else:
            config = cls(key=key, value=str(value))
            db.session.add(config)
        db.session.commit()

class Subject(db.Model):
    """Academic subject assigned to a program and semester"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Assigned faculty
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    program = db.relationship('Program', backref=db.backref('subjects', lazy=True))
    faculty = db.relationship('User', foreign_keys=[faculty_id], backref=db.backref('assigned_subjects', lazy=True))

class InternalMarks(db.Model):
    """Internal marks for a student in a subject"""
    __tablename__ = 'internal_marks'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    marks = db.Column(db.Float, nullable=True) # Can be null if not yet entered
    max_marks = db.Column(db.Float, default=30.0) # Default to 30
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('User', foreign_keys=[student_id], backref=db.backref('marks', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('marks', lazy=True))
    
    # Ensure one entry per student per subject
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='_student_subject_uc'),)

class SubjectFeedback(db.Model):
    """Student feedback for a subject/faculty"""
    __tablename__ = 'subject_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5 scale
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subject = db.relationship('Subject', backref=db.backref('feedbacks', lazy=True))
    student = db.relationship('User', foreign_keys=[student_id])
    
    # Ensure one feedback per student per subject
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', name='_student_feedback_uc'),)
