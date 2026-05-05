from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from models import db, Event, Department, User, Attendance
from datetime import datetime, date
import secrets

common_bp = Blueprint('common', __name__)


@common_bp.route('/')
def index():
    """Landing page with QR code for registration"""
    # Redirect logged-in users to their dashboards
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'Faculty':
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student.dashboard'))
        elif current_user.role == 'Counselor':
            return redirect(url_for('counselor.dashboard'))
    
    # Generate a unique QR token for registration
    qr_token = secrets.token_urlsafe(16)
    
    # Get upcoming public events
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_events': Event.query.count(),
        'total_departments': Department.query.count(),
        'attendance_today': Attendance.query.filter(
            db.func.date(Attendance.timestamp) == date.today()
        ).count()
    }
    
    return render_template('common/index.html',
                         qr_token=qr_token,
                         upcoming_events=upcoming_events,
                         stats=stats)


@common_bp.route('/visitor')
def visitor():
    """Visitor information page"""
    # Generate a unique QR token for registration
    qr_token = secrets.token_urlsafe(16)
    
    # Get all departments
    departments = Department.query.all()
    
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_events': Event.query.count(),
        'total_departments': Department.query.count()
    }
    
    return render_template('common/visitor.html',
                         qr_token=qr_token,
                         departments=departments,
                         stats=stats)


@common_bp.route('/visitor-kiosk')
def visitor_kiosk():
    """Self-service visitor check-in kiosk"""
    return render_template('common/visitor_kiosk.html')


@common_bp.route('/face-recognition')
def face_recognition():
    """Face recognition interface"""
    from models import User
    # Get all students for manual selection
    students = User.query.filter_by(role='Student', is_active=True).order_by(User.full_name).all()
    return render_template('common/face_recognition.html', students=students)


@common_bp.route('/auto-attendance')
def auto_attendance():
    """Automatic attendance detection interface"""
    return render_template('common/auto_attendance.html')


@common_bp.route('/voice-chat')
def voice_chat():
    """Voice-to-voice chat interface"""
    return render_template('common/voice_chat.html')


@common_bp.route('/info')
def info():
    """Public campus information"""
    departments = Department.query.all()
    total_events = Event.query.count()
    
    return render_template('common/info.html',
                         departments=departments,
                         total_events=total_events)

