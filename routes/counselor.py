from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, EmotionTracking
from models.student_tracking import StudentTracking
from datetime import datetime, timedelta
import pytz
from functools import wraps

counselor_bp = Blueprint('counselor', __name__)

def counselor_required(f):
    """Decorator to require counselor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('counselor.login'))
        if current_user.role != 'Counselor':
            flash('Access denied. Counselors only.', 'danger')
            return redirect(url_for('common.index'))
        return f(*args, **kwargs)
    return decorated_function

@counselor_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Counselor login"""
    if current_user.is_authenticated and current_user.role == 'Counselor':
        return redirect(url_for('counselor.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role != 'Counselor':
                flash('This login is for counselors only.', 'danger')
                return redirect(url_for('counselor.login'))
            
            login_user(user)
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('counselor.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('counselor/login.html')

@counselor_bp.route('/logout')
@login_required
def logout():
    """Counselor logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('counselor.login'))

@counselor_bp.route('/dashboard')
@login_required
@counselor_required
def dashboard():
    """Counselor dashboard showing sad students"""
    return render_template('counselor/dashboard.html')

@counselor_bp.route('/api/sad-students')
@login_required
@counselor_required
def get_sad_students():
    """Get students detected as sad for 2+ consecutive days"""
    try:
        # Get all students
        students = User.query.filter_by(role='Student').all()
        sad_students = []
        
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).date()
        
        for student in students:
            # Get emotion tracking records for the last 7 days
            records = EmotionTracking.query.filter(
                EmotionTracking.user_id == student.id,
                EmotionTracking.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).order_by(EmotionTracking.timestamp.desc()).all()
            
            # Analyze for consecutive sad days
            sad_days = set()
            recent_emotions = []
            
            for record in records:
                # Convert to IST date
                record_date = record.timestamp.replace(tzinfo=pytz.UTC).astimezone(ist).date()
                emotion = record.dominant_emotion.lower()
                
                recent_emotions.append({
                    'date': record_date.strftime('%Y-%m-%d'),
                    'emotion': emotion,
                    'confidence': record.confidence
                })
                
                if emotion == 'sad':
                    sad_days.add(record_date)
            
            # Check for consecutive days
            is_alert = False
            sorted_sad_days = sorted(list(sad_days), reverse=True)
            
            if len(sorted_sad_days) >= 2:
                for i in range(len(sorted_sad_days) - 1):
                    # Check if days are consecutive (diff is 1 day)
                    if (sorted_sad_days[i] - sorted_sad_days[i+1]).days == 1:
                        is_alert = True
                        break
            
            if is_alert:
                sad_students.append({
                    'id': student.id,
                    'name': student.full_name,
                    'registration_id': student.registration_id,
                    'department': student.department.name if student.department else 'N/A',
                    'program': student.program.name if student.program else 'N/A',
                    'year': student.year,
                    'profile_picture': student.profile_picture,
                    'sad_days_count': len(sad_days),
                    'recent_emotions': recent_emotions[:5]  # Last 5 emotion records
                })
        
        return jsonify({
            'success': True,
            'count': len(sad_students),
            'students': sad_students
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
