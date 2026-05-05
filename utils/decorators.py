from flask_login import LoginManager, current_user
from functools import wraps
from flask import redirect, url_for, flash, abort

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'


def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            if not current_user.is_approved:
                flash('Your account is pending approval.', 'warning')
                return redirect(url_for('auth.pending_approval'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role"""
    return role_required('Admin')(f)


def student_required(f):
    """Decorator to require student role"""
    return role_required('Student')(f)


def faculty_required(f):
    """Decorator to require faculty role"""
    return role_required('Faculty')(f)
