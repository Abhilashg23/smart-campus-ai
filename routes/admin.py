from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, User, Event, PendingRegistration, Department, Attendance, SystemConfig, Subject, InternalMarks, Program
from utils.decorators import admin_required
from utils.helpers import save_uploaded_file
from datetime import datetime
import os
import io
from openpyxl import Workbook
from flask import send_file
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts
    total_users = User.query.count()
    total_events = Event.query.count()
    total_departments = Department.query.count()
    pending_registrations = PendingRegistration.query.filter_by(status='pending').count()
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    # Get anonymous messages count (with error handling)
    pending_messages = 0
    try:
        from models.anonymous_message import AnonymousMessage
        pending_messages = AnonymousMessage.query.filter_by(status='pending').count()
    except Exception as e:
        print(f"Error fetching anonymous messages: {e}")
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_events=total_events,
                         total_departments=total_departments,
                         pending_registrations=pending_registrations,
                         pending_messages=pending_messages,
                         recent_events=recent_events)


@admin_bp.route('/events')
@login_required
@admin_required
def events():
    """View all events"""
    all_events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', events=all_events)


@admin_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    """Create new event"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date = request.form.get('event_date')
        location = request.form.get('location')
        department_id = request.form.get('department_id')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path = save_uploaded_file(file, 'events', {'png', 'jpg', 'jpeg', 'gif'})
        
        # Create event
        event = Event(
            title=title,
            description=description,
            event_date=datetime.strptime(event_date, '%Y-%m-%dT%H:%M'),
            location=location,
            created_by=current_user.id,
            department_id=department_id if department_id else None,
            image_path=image_path
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('admin.events'))
    
    departments = Department.query.all()
    return render_template('admin/create_event.html', departments=departments)


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Edit existing event"""
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M')
        event.location = request.form.get('location')
        event.department_id = request.form.get('department_id') if request.form.get('department_id') else None
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_path = save_uploaded_file(file, 'events', {'png', 'jpg', 'jpeg', 'gif'})
                event.image_path = image_path
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin.events'))
    
    departments = Department.query.all()
    return render_template('admin/edit_event.html', event=event, departments=departments)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Delete event"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """View all users"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Handle profile picture upload
        profile_picture_path = None
        face_encoding_data = None
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Import utilities
                from utils.process_profile_image import validate_image_file, extract_face_encoding, encoding_to_bytes
                from models import FaceData
                
                # Validate image
                is_valid, error_msg = validate_image_file(file)
                if not is_valid:
                    flash(f'Image validation failed: {error_msg}', 'danger')
                    return redirect(url_for('admin.add_user'))
                
                # Extract face encoding
                success, encoding, error_msg = extract_face_encoding(file)
                if not success:
                    flash(f'Face detection failed: {error_msg}', 'danger')
                    return redirect(url_for('admin.add_user'))
                
                # Save image file
                filename = secure_filename(file.filename)
                # Create unique filename with timestamp
                import time
                timestamp = str(int(time.time()))
                filename = f"{username}_{timestamp}_{filename}"
                
                # Create directory if it doesn't exist
                upload_dir = os.path.join('static', 'images', 'students')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Store path for database
                profile_picture_path = f"/static/images/students/{filename}"
                
                # Convert encoding to bytes for storage
                face_encoding_data = encoding_to_bytes(encoding)
        
        # Validate student-specific fields if role is Student
        if role == 'Student':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            registration_id = request.form.get('registration_id')
            program_id = request.form.get('program_id')
            custom_program = request.form.get('custom_program')
            year = request.form.get('year')
            semester = request.form.get('semester')
            section = request.form.get('section')
            
            # Handle custom program entry
            if program_id == 'other':
                if not custom_program:
                    flash('Please enter a custom program name!', 'danger')
                    return redirect(url_for('admin.add_user'))
                
                # Create new program with custom name
                from models import Program
                # Use the selected department or default to first available
                dept_id = department_id if department_id else Department.query.first().id
                
                # Generate a unique code from the program name
                import re
                code_base = re.sub(r'[^A-Za-z0-9]+', '-', custom_program.upper())[:20]
                code = code_base
                counter = 1
                while Program.query.filter_by(code=code).first():
                    code = f"{code_base}-{counter}"
                    counter += 1
                
                new_program = Program(
                    name=custom_program,
                    code=code,
                    department_id=dept_id,
                    duration_years=4  # Default duration
                )
                db.session.add(new_program)
                db.session.flush()  # Get the ID
                program_id = str(new_program.id)
                flash(f'New program "{custom_program}" created successfully!', 'info')
            
            # Check if all student fields are provided
            if not all([first_name, last_name, registration_id, program_id, year, semester, section]):
                flash('All student fields are required for Student role!', 'danger')
                return redirect(url_for('admin.add_user'))
            
            # Check if registration_id already exists
            if User.query.filter_by(registration_id=registration_id).first():
                flash('Registration ID already exists!', 'danger')
                return redirect(url_for('admin.add_user'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            department_id=department_id if department_id else None,
            profile_picture=profile_picture_path,
            is_approved=True
        )
        user.set_password(password)
        
        # Add student-specific fields if role is Student
        if role == 'Student':
            user.first_name = first_name
            user.last_name = last_name
            user.registration_id = registration_id
            user.program_id = int(program_id)
            user.year = int(year)
            user.semester = int(semester)
            user.section = section
        
        db.session.add(user)
        db.session.flush()  # Get user ID before commit
        
        # Save face encoding if available
        if face_encoding_data:
            from models import FaceData
            face_data = FaceData(
                user_id=user.id,
                face_encoding=face_encoding_data,
                image_path=profile_picture_path
            )
            db.session.add(face_data)
        
        db.session.commit()
        
        if face_encoding_data:
            # Reload face recognition service to include new face
            from services.face_recognition import face_recognition_service
            face_recognition_service.load_known_faces()
            flash(f'User added successfully with face recognition enabled!', 'success')
        else:
            flash('User added successfully!', 'success')
        
        return redirect(url_for('admin.users'))
    
    from models import Program
    departments = Department.query.all()
    programs = Program.query.all()
    return render_template('admin/add_user.html', departments=departments, programs=programs)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.role = request.form.get('role')
        user.department_id = request.form.get('department_id') if request.form.get('department_id') else None
        
        # Update password if provided
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create unique filename with timestamp
                import time
                timestamp = str(int(time.time()))
                role_folder = user.role.lower() + 's' if user.role != 'Admin' else 'admin'
                filename = f"{user.username}_{timestamp}_{filename}"
                
                # Create directory if it doesn't exist
                upload_dir = os.path.join('static', 'images', role_folder)
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Update database path
                user.profile_picture = f"/static/images/{role_folder}/{filename}"
                
                # Handle face enrollment if checkbox is checked
                enroll_face = request.form.get('enroll_face')
                if enroll_face:
                    try:
                        # Read the image file for face enrollment
                        file.seek(0)  # Reset file pointer
                        image_data = file.read()
                        
                        # Save to face data folder as well
                        from services.face_recognition import face_recognition_service
                        face_data_dir = current_app.config.get('FACE_DATA_FOLDER', 'face_data')
                        os.makedirs(face_data_dir, exist_ok=True)
                        face_image_path = os.path.join(face_data_dir, f"{user.id}_{filename}")
                        
                        # Save image to face data folder
                        with open(face_image_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Enroll face
                        success, message = face_recognition_service.enroll_face(
                            image_data,
                            user.id,
                            face_image_path
                        )
                        
                        if success:
                            flash(f'User updated and face enrolled successfully! {message}', 'success')
                        else:
                            flash(f'User updated but face enrollment failed: {message}', 'warning')
                    except Exception as e:
                        print(f"Error enrolling face: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        flash(f'User updated but face enrollment failed: {str(e)}', 'warning')
                else:
                    flash('User updated successfully!', 'success')
        else:
            flash('User updated successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.users'))
    
    departments = Department.query.all()
    return render_template('admin/edit_user.html', user=user, departments=departments)



@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if new_password:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Password reset successfully for {user.username}!', 'success')
    else:
        flash('Password cannot be empty!', 'danger')
    
    return redirect(url_for('admin.users'))



@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    """View all departments"""
    all_departments = Department.query.all()
    return render_template('admin/departments.html', departments=all_departments)


@admin_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    """Add new department"""
    if request.method == 'POST':
        name = request.form.get('name')
        head_of_department = request.form.get('head_of_department')
        contact_email = request.form.get('contact_email')
        contact_phone = request.form.get('contact_phone')
        
        department = Department(
            name=name,
            head_of_department=head_of_department,
            contact_email=contact_email,
            contact_phone=contact_phone
        )
        
        db.session.add(department)
        db.session.commit()
        
        flash('Department added successfully!', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/add_department.html')


@admin_bp.route('/pending-registrations')
@login_required
@admin_required
def pending_registrations():
    """View pending registrations"""
    # Get pending registrations from pending_registrations table
    pending = PendingRegistration.query.filter_by(status='pending').all()
    
    # Also get unapproved users from users table
    unapproved_users = User.query.filter_by(is_approved=False).all()
    
    # Combine both lists for display
    return render_template('admin/pending_registrations.html', 
                         pending_registrations=pending,
                         unapproved_users=unapproved_users)


@admin_bp.route('/pending-registrations/<int:reg_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_registration(reg_id):
    """Approve pending registration"""
    pending = PendingRegistration.query.get_or_404(reg_id)
    
    # Create actual user
    user = User(
        username=pending.username,
        email=pending.email,
        password_hash=pending.password_hash,
        full_name=pending.full_name,
        role=pending.role,
        department_id=pending.department_id,
        is_approved=True
    )
    
    db.session.add(user)
    pending.status = 'approved'
    db.session.commit()
    
    flash(f'Registration approved for {pending.username}!', 'success')
    return redirect(url_for('admin.pending_registrations'))


@admin_bp.route('/pending-registrations/<int:reg_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_registration(reg_id):
    """Reject pending registration"""
    pending = PendingRegistration.query.get_or_404(reg_id)
    pending.status = 'rejected'
    db.session.commit()
    
    flash(f'Registration rejected for {pending.username}.', 'info')
    return redirect(url_for('admin.pending_registrations'))


@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    """Approve an unapproved user"""
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'User {user.username} has been approved!', 'success')
    return redirect(url_for('admin.pending_registrations'))


@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    """Reject/delete an unapproved user"""
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been rejected and removed.', 'info')
    return redirect(url_for('admin.pending_registrations'))


@admin_bp.route('/classes')
@login_required
@admin_required
def classes():
    """View class-faculty-student mappings"""
    departments = Department.query.all()
    return render_template('admin/classes.html', departments=departments)


# Faculty Management Routes
@admin_bp.route('/faculty')
@login_required
@admin_required
def manage_faculty():
    """Manage faculty profiles"""
    # Get filter parameters
    search_query = request.args.get('search', '')
    department_id = request.args.get('department_id', type=int)
    sort_by = request.args.get('sort_by', 'name')  # name, department
    
    # Base query
    query = User.query.filter_by(role='Faculty')
    
    # Apply search filter
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.designation.ilike(search_term)
            )
        )
    
    # Apply department filter
    if department_id:
        query = query.filter_by(department_id=department_id)
        
    # Apply sorting
    if sort_by == 'department':
        query = query.join(Department, isouter=True).order_by(Department.name.asc(), User.full_name.asc())
    else:
        query = query.order_by(User.full_name.asc())
        
    faculty_list = query.all()
    departments = Department.query.order_by(Department.name.asc()).all()
    
    return render_template('admin/manage_faculty.html', 
                         faculty_list=faculty_list,
                         departments=departments,
                         search_query=search_query,
                         selected_department_id=department_id,
                         sort_by=sort_by)


@admin_bp.route('/faculty/<int:faculty_id>/update', methods=['POST'])
@login_required
@admin_required
def update_faculty(faculty_id):
    """Update faculty profile"""
    faculty = User.query.get_or_404(faculty_id)
    
    # Update basic info
    faculty.full_name = request.form.get('full_name')
    faculty.email = request.form.get('email')
    faculty.designation = request.form.get('designation')
    faculty.department_id = request.form.get('department_id') if request.form.get('department_id') else None
    faculty.education = request.form.get('education')
    faculty.bio = request.form.get('bio')
    faculty.research_interests = request.form.get('research_interests')
    faculty.university_profile_url = request.form.get('university_profile_url')
    
        # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            # Import utilities
            from utils.process_profile_image import validate_image_file, extract_face_encoding, encoding_to_bytes
            from models import FaceData
            
            # Validate image
            is_valid, error_msg = validate_image_file(file)
            if not is_valid:
                flash(f'Image validation failed: {error_msg}', 'danger')
                return redirect(url_for('admin.manage_faculty'))
            
            # Extract face encoding
            # We need to save the file pointer position to reset it after reading
            file.seek(0)
            success, encoding, error_msg = extract_face_encoding(file)
            
            # Reset file pointer for saving
            file.seek(0)
            
            if not success:
                flash(f'Face detection failed: {error_msg}', 'warning')
                # We still allow the update but warn the user
            
            # Create safe filename
            filename = secure_filename(file.filename)
            # Create valid unique filename
            import time
            timestamp = str(int(time.time()))
            filename = f"{faculty.username}_{timestamp}_{filename}"
            
            # Create directory if it doesn't exist
            upload_dir = os.path.join('static', 'images', 'faculty', 'engineering')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Update database paths (update both fields for consistency)
            relative_path = f"/static/images/faculty/engineering/{filename}"
            faculty.profile_image = relative_path
            faculty.profile_picture = relative_path
            
            # If face encoding was successful, update face data
            if success:
                try:
                    # Convert to bytes
                    face_encoding_bytes = encoding_to_bytes(encoding)
                    
                    # Check if face data exists
                    face_data = FaceData.query.filter_by(user_id=faculty.id).first()
                    
                    if face_data:
                        face_data.face_encoding = face_encoding_bytes
                        face_data.image_path = relative_path
                    else:
                        face_data = FaceData(
                            user_id=faculty.id,
                            face_encoding=face_encoding_bytes,
                            image_path=relative_path
                        )
                        db.session.add(face_data)
                    
                    # Store changes to commit below
                    db.session.flush()
                    
                    # Reload face recognition service
                    try:
                        from services.face_recognition import face_recognition_service
                        face_recognition_service.load_known_faces()
                        flash(f'Profile and face recognition updated for {faculty.full_name}!', 'success')
                    except Exception as e:
                        print(f"Error reloading faces: {e}")
                        flash(f'Profile updated but error reloading recognition service: {e}', 'warning')
                        
                except Exception as e:
                    print(f"Error updating face data: {e}")
                    flash(f'Profile updated but face data error: {e}', 'warning')
            else:
                flash(f'Profile picture updated but face not enrolled: {error_msg}', 'warning')
    
    db.session.commit()
    # If we didn't update the image, we still need to flash success for other fields
    if 'profile_image' not in request.files or not request.files['profile_image'].filename:
        flash(f'Profile updated for {faculty.full_name}!', 'success')
        
    return redirect(url_for('admin.manage_faculty'))


@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    """Admin profile page with edit functionality"""
    if request.method == 'POST':
        # Update basic info
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create unique filename with timestamp
                import time
                timestamp = str(int(time.time()))
                filename = f"admin_{current_user.username}_{timestamp}_{filename}"
                
                # Create directory if it doesn't exist
                upload_dir = os.path.join('static', 'images', 'admin')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Update database path
                current_user.profile_picture = f"/static/images/admin/{filename}"
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
    
    return render_template('admin/profile.html')


@admin_bp.route('/anonymous-messages')
@login_required
@admin_required
def anonymous_messages():
    """View anonymous messages/complaints"""
    from models.anonymous_message import AnonymousMessage
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    # Build query
    query = AnonymousMessage.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # Get messages ordered by newest first
    messages = query.order_by(AnonymousMessage.timestamp.desc()).all()
    
    # Get counts for dashboard
    total_messages = AnonymousMessage.query.count()
    pending_count = AnonymousMessage.query.filter_by(status='pending').count()
    reviewed_count = AnonymousMessage.query.filter_by(status='reviewed').count()
    resolved_count = AnonymousMessage.query.filter_by(status='resolved').count()
    
    return render_template('admin/anonymous_messages.html',
                         messages=messages,
                         total_messages=total_messages,
                         pending_count=pending_count,
                         reviewed_count=reviewed_count,
                         resolved_count=resolved_count,
                         status_filter=status_filter,
                         category_filter=category_filter)


@admin_bp.route('/marks-config', methods=['GET', 'POST'])
@login_required
@admin_required
def marks_config():
    """Admin configuration for internal marks upload"""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'lock':
            SystemConfig.set_value('marks_upload_locked', 'true')
            flash('Marks upload has been LOCKED for all faculties.', 'warning')
        elif action == 'unlock':
            SystemConfig.set_value('marks_upload_locked', 'false')
            flash('Marks upload has been UNLOCKED for all faculties.', 'success')
        return redirect(url_for('admin.marks_config'))
        
    is_locked = SystemConfig.get_value('marks_upload_locked', 'false') == 'true'
    
    # Also get stats for display
    total_subjects = Subject.query.count()
    total_marks_entered = InternalMarks.query.filter(InternalMarks.marks.isnot(None)).count()
    
    return render_template('admin/marks_config.html', 
                          is_locked=is_locked, 
                          total_subjects=total_subjects,
                          total_marks_entered=total_marks_entered)


@admin_bp.route('/marks-download')
@login_required
@admin_required
def marks_download():
    """Download all internal marks as Excel"""
    marks_records = InternalMarks.query.join(Subject).join(User, InternalMarks.student_id == User.id).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Internal Marks"
    
    # Headers
    headers = ['Student ID', 'Student Name', 'Program', 'Semester', 'Subject Code', 'Subject Name', 'Marks', 'Max Marks', 'Faculty Name']
    ws.append(headers)
    
    for record in marks_records:
        student = record.student
        subject = record.subject
        faculty = subject.faculty
        program = subject.program
        
        ws.append([
            student.registration_id or student.username,
            student.full_name,
            program.name if program else 'N/A',
            subject.semester,
            subject.code,
            subject.name,
            record.marks if record.marks is not None else 'Not Entered',
            record.max_marks,
            faculty.full_name if faculty else 'N/A'
        ])
    
    # Save to memory
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'internal_marks_export_{timestamp}.xlsx'
    )


@admin_bp.route('/feedback')
@login_required
@admin_required
def feedback():
    """Admin view: all student feedback across all faculty/subjects"""
    from models import SubjectFeedback
    from sqlalchemy import func

    # All feedback with related info
    all_feedbacks = SubjectFeedback.query.order_by(SubjectFeedback.created_at.desc()).all()

    # Per-faculty summary
    faculty_summary = {}
    for fb in all_feedbacks:
        subj = fb.subject
        if not subj:
            continue
        fac_id = subj.faculty_id
        if fac_id not in faculty_summary:
            fac = User.query.get(fac_id)
            faculty_summary[fac_id] = {
                'faculty': fac,
                'total': 0,
                'rating_sum': 0,
                'subjects': set()
            }
        faculty_summary[fac_id]['total'] += 1
        faculty_summary[fac_id]['rating_sum'] += fb.rating
        faculty_summary[fac_id]['subjects'].add(subj.id)

    # Convert to sorted list
    faculty_list = []
    for fac_id, data in faculty_summary.items():
        avg = round(data['rating_sum'] / data['total'], 1) if data['total'] else 0
        faculty_list.append({
            'faculty': data['faculty'],
            'total_responses': data['total'],
            'avg_rating': avg,
            'subject_count': len(data['subjects'])
        })
    faculty_list.sort(key=lambda x: x['avg_rating'], reverse=True)

    overall_avg = round(sum(f.rating for f in all_feedbacks) / len(all_feedbacks), 1) if all_feedbacks else 0

    return render_template('admin/feedback.html',
                           all_feedbacks=all_feedbacks,
                           faculty_list=faculty_list,
                           overall_avg=overall_avg,
                           total_responses=len(all_feedbacks))
