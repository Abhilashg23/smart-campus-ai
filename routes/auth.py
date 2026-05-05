from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, PendingRegistration
from utils.helpers import is_valid_email, is_strong_password
import secrets

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'Student':
            return redirect(url_for('student.dashboard'))
        elif current_user.role == 'Faculty':
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == 'Security':
            return redirect(url_for('security.dashboard'))
        elif current_user.role == 'SecurityAdmin':
            return redirect(url_for('security.admin_dashboard'))
        elif current_user.role == 'Counselor':
            return redirect(url_for('counselor.dashboard'))
        elif current_user.role == 'VisitorEntry':
            return redirect(url_for('visitor_entry.dashboard'))
        else:
            return redirect(url_for('common.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_approved:
                flash('Your account is pending approval by an administrator.', 'warning')
                return redirect(url_for('auth.pending_approval'))
            
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect based on role
            if user.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'Student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'Faculty':
                return redirect(url_for('faculty.dashboard'))
            elif user.role == 'Security':
                return redirect(url_for('security.dashboard'))
            elif user.role == 'SecurityAdmin':
                return redirect(url_for('security.admin_dashboard'))
            elif user.role == 'Counselor':
                return redirect(url_for('counselor.dashboard'))
            elif user.role == 'VisitorEntry':
                return redirect(url_for('visitor_entry.dashboard'))
            else:
                return redirect(url_for('common.index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('common.index'))


@auth_bp.route('/register/<qr_token>', methods=['GET', 'POST'])
def register(qr_token):
    """QR-based user registration"""
    # Verify QR token is valid (for now, accept any token)
    # In production, validate against a generated token
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        
        # Validation
        if not all([username, email, password, confirm_password, full_name, role]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        if not is_valid_email(email):
            flash('Invalid email address.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        is_strong, message = is_strong_password(password)
        if not is_strong:
            flash(message, 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        if PendingRegistration.query.filter_by(username=username).first():
            flash('Username already pending approval.', 'danger')
            return render_template('auth/register.html', qr_token=qr_token)
        
        # Create pending registration
        pending = PendingRegistration(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            qr_token=qr_token
        )
        pending.set_password(password)
        
        db.session.add(pending)
        db.session.commit()
        
        flash('Registration submitted! Please wait for admin approval.', 'success')
        return redirect(url_for('auth.pending_approval'))
    
    return render_template('auth/register.html', qr_token=qr_token)


@auth_bp.route('/pending-approval')
def pending_approval():
    """Page shown to users awaiting approval"""
    return render_template('auth/pending_approval.html')


@auth_bp.route('/check-approval/<username>')
def check_approval(username):
    """API endpoint to check if registration is approved"""
    user = User.query.filter_by(username=username).first()
    if user and user.is_approved:
        return {'approved': True}
    return {'approved': False}
