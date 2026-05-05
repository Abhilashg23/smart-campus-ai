from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from models.student_tracking import StudentTracking
from datetime import datetime, timedelta
import pytz
from functools import wraps

security_bp = Blueprint('security', __name__)


def security_required(f):
    """Decorator to require security role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('security.login'))
        if current_user.role not in ['Security', 'SecurityAdmin']:
            flash('Access denied. Security personnel only.', 'danger')
            return redirect(url_for('common.index'))
        return f(*args, **kwargs)
    return decorated_function


@security_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Security personnel login"""
    if current_user.is_authenticated and current_user.role == 'Security':
        return redirect(url_for('security.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role != 'Security':
                flash('This login is for security personnel only.', 'danger')
                return redirect(url_for('security.login'))
            
            if not user.is_approved:
                flash('Your account is pending approval.', 'warning')
                return redirect(url_for('security.login'))
            
            if not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('security.login'))
            
            login_user(user)
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('security.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('security/login.html')


@security_bp.route('/logout')
@login_required
def logout():
    """Security logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('security.login'))


@security_bp.route('/dashboard')
@login_required
@security_required
def dashboard():
    """Security student tracking dashboard"""
    return render_template('security/dashboard.html')


@security_bp.route('/tracking-history')
@login_required
@security_required
def tracking_history():
    """View all student tracking history"""
    return render_template('security/tracking_history.html')


@security_bp.route('/entry-exit-view')
@login_required
@security_required
def entry_exit_view():
    """View IN and OUT entries separately"""
    return render_template('security/entry_exit_view.html')


@security_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    """Security Admin unified dashboard - student/faculty tracking + visitor management"""
    if current_user.role != 'SecurityAdmin':
        flash('Access denied. Security Admin only.', 'danger')
        return redirect(url_for('common.index'))
    
    # Get visitor statistics
    from services.visitor_service import visitor_service
    visitor_stats = visitor_service.get_visitor_stats()
    active_visitors = visitor_service.get_active_visitors()
    
    return render_template('security/admin_dashboard.html',
                         visitor_stats=visitor_stats,
                         active_visitors=active_visitors)


@security_bp.route('/api/student-tracking')
@login_required
@security_required
def student_tracking():
    """Get today's student tracking records"""
    try:
        # Use Indian Standard Time
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        today = now_ist.date()
        
        # Get all tracking records for today
        tracking_records = StudentTracking.query.filter(
            db.func.date(StudentTracking.timestamp) == today
        ).order_by(StudentTracking.timestamp.desc()).all()
        
        # Format the data
        tracking_list = []
        for record in tracking_records:
            user = record.user
            # Convert UTC timestamp to IST
            utc_time = record.timestamp.replace(tzinfo=pytz.UTC)
            ist_time = utc_time.astimezone(ist)
            
            tracking_list.append({
                'id': record.id,
                'user_id': user.id,
                'name': user.full_name or f"{user.first_name} {user.last_name}",
                'registration_id': user.registration_id or 'N/A',
                'role': user.role,
                'entry_type': record.entry_type,
                'time': ist_time.strftime('%I:%M %p'),
                'location': record.location
            })
        
        return jsonify({
            'success': True,
            'count': len(tracking_list),
            'tracking': tracking_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@security_bp.route('/api/tracking-history-data')
@login_required
@security_required
def tracking_history_data():
    """Get all student tracking history with optional filters"""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Base query
        query = StudentTracking.query.join(User)
        
        # Apply search filter
        if search:
            query = query.filter(
                db.or_(
                    User.full_name.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%'),
                    User.registration_id.ilike(f'%{search}%')
                )
            )
        
        # Apply date filters
        ist = pytz.timezone('Asia/Kolkata')
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(StudentTracking.timestamp) >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(StudentTracking.timestamp) <= end)
        
        # Get records ordered by timestamp descending
        tracking_records = query.order_by(StudentTracking.timestamp.desc()).all()
        
        # Format the data
        tracking_list = []
        for record in tracking_records:
            user = record.user
            # Convert UTC timestamp to IST
            utc_time = record.timestamp.replace(tzinfo=pytz.UTC)
            ist_time = utc_time.astimezone(ist)
            
            tracking_list.append({
                'id': record.id,
                'user_id': user.id,
                'name': user.full_name or f"{user.first_name} {user.last_name}",
                'registration_id': user.registration_id or 'N/A',
                'role': user.role,
                'entry_type': record.entry_type,
                'date': ist_time.strftime('%B %d, %Y'),
                'time': ist_time.strftime('%I:%M %p'),
                'location': record.location
            })
        
        return jsonify({
            'success': True,
            'count': len(tracking_list),
            'tracking': tracking_list
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
