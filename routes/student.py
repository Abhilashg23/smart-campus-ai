from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Event, ChatHistory, Attendance, Subject, InternalMarks, SubjectFeedback
from utils.decorators import student_required
from datetime import datetime

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).limit(5).all()
    
    return render_template('student/dashboard.html',
                         student_name=current_user.full_name,
                         upcoming_events=upcoming_events)


@student_bp.route('/events')
@login_required
@student_required
def events():
    """View all upcoming events"""
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).all()
    
    return render_template('student/events.html', events=upcoming_events)


@student_bp.route('/profile')
@login_required
@student_required
def profile():
    """Student profile page"""
    # Get attendance count
    attendance_count = Attendance.query.filter_by(user_id=current_user.id).count()
    
    # Get events count (could be registrations or attended events)
    event_count = Event.query.filter(Event.event_date >= datetime.utcnow()).count()
    
    return render_template('student/profile.html',
                         attendance_count=attendance_count,
                         event_count=event_count)


@student_bp.route('/chat')
@login_required
@student_required
def chat():
    """Chatbot interface"""
    return render_template('student/chat.html')


@student_bp.route('/chat/history')
@login_required
@student_required
def chat_history():
    """View chat history"""
    history = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('student/chat_history.html', history=history)


@student_bp.route('/marks')
@login_required
@student_required
def marks():
    """View internal marks for enrolled subjects"""
    if not current_user.program_id or not current_user.semester:
        flash('You are not assigned to a program and semester yet.', 'warning')
        return render_template('student/view_marks.html', subjects_marks=[])
        
    # Get subjects for the student's program and semester
    subjects = Subject.query.filter_by(
        program_id=current_user.program_id, 
        semester=current_user.semester
    ).all()
    
    # Pre-fetch marks
    marks_records = InternalMarks.query.filter_by(student_id=current_user.id).all()
    marks_dict = {m.subject_id: m for m in marks_records}
    
    subjects_marks = []
    for subject in subjects:
        mark_record = marks_dict.get(subject.id)
        subjects_marks.append({
            'subject': subject,
            'mark': mark_record.marks if mark_record and mark_record.marks is not None else 'Not Entered',
            'max_marks': mark_record.max_marks if mark_record else 30.0
        })
        
    return render_template('student/view_marks.html', subjects_marks=subjects_marks)


@student_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
@student_required
def feedback():
    """Submit feedback for enrolled subjects/faculty"""
    # Get subjects via InternalMarks enrolment (correct approach)
    enrolled = InternalMarks.query.filter_by(student_id=current_user.id).all()
    subject_ids = list({r.subject_id for r in enrolled})
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all() if subject_ids else []

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments', '').strip()

        if subject_id and rating:
            try:
                subject_id = int(subject_id)
                rating = int(rating)
                if not (1 <= rating <= 5):
                    flash('Rating must be between 1 and 5.', 'danger')
                    return redirect(url_for('student.feedback'))

                existing = SubjectFeedback.query.filter_by(
                    student_id=current_user.id, subject_id=subject_id
                ).first()
                if existing:
                    existing.rating = rating
                    existing.comments = comments
                    db.session.commit()
                    flash('Your feedback has been updated!', 'success')
                else:
                    fb = SubjectFeedback(
                        student_id=current_user.id,
                        subject_id=subject_id,
                        rating=rating,
                        comments=comments
                    )
                    db.session.add(fb)
                    db.session.commit()
                    flash('Thank you! Feedback submitted successfully.', 'success')
            except (ValueError, TypeError):
                flash('Invalid input. Please try again.', 'danger')
        return redirect(url_for('student.feedback'))

    # Build feedback context
    existing_feedbacks = {
        f.subject_id: f
        for f in SubjectFeedback.query.filter_by(student_id=current_user.id).all()
    }

    subjects_feedback = []
    for subject in subjects:
        subjects_feedback.append({
            'subject': subject,
            'existing': existing_feedbacks.get(subject.id),
            'submitted': subject.id in existing_feedbacks
        })

    subjects_feedback.sort(key=lambda x: x['submitted'])

    return render_template('student/submit_feedback.html', subjects_feedback=subjects_feedback)

