"""
Visitor Entry authenticated routes
Requires login with VisitorEntry role
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from utils.decorators import role_required
from services.visitor_service import visitor_service

visitor_entry_bp = Blueprint('visitor_entry', __name__)


@visitor_entry_bp.route('/dashboard')
@login_required
@role_required('VisitorEntry', 'SecurityAdmin')
def dashboard():
    """Visitor entry dashboard - shows active visitors"""
    active_visitors = visitor_service.get_active_visitors()
    stats = visitor_service.get_visitor_stats()
    
    return render_template('visitor_entry/dashboard.html',
                         active_visitors=active_visitors,
                         stats=stats)


@visitor_entry_bp.route('/history')
@login_required
@role_required('VisitorEntry', 'SecurityAdmin')
def history():
    """Visitor history view"""
    days = 30  # Default to 30 days
    visitors = visitor_service.get_visitor_history(days)
    
    return render_template('visitor_entry/history.html',
                         visitors=visitors,
                         days=days)


@visitor_entry_bp.route('/manual-entry')
@login_required
@role_required('VisitorEntry', 'SecurityAdmin')
def manual_entry():
    """Manual visitor entry form"""
    return render_template('visitor_entry/manual_entry.html')
