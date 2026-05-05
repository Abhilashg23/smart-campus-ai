from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.anonymous_message import AnonymousMessage
from datetime import datetime

anonymous_api_bp = Blueprint('anonymous_api', __name__)


@anonymous_api_bp.route('/submit', methods=['POST'])
def submit_message():
    """Submit an anonymous message/complaint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message is required'
            }), 400
        
        message_text = data.get('message', '').strip()
        category = data.get('category', 'other').strip()
        
        # Validate message length
        if len(message_text) < 10:
            return jsonify({
                'success': False,
                'message': 'Message must be at least 10 characters long'
            }), 400
        
        if len(message_text) > 2000:
            return jsonify({
                'success': False,
                'message': 'Message must not exceed 2000 characters'
            }), 400
        
        # Validate category
        valid_categories = ['complaint', 'suggestion', 'feedback', 'other']
        if category not in valid_categories:
            category = 'other'
        
        # Create new anonymous message
        anonymous_msg = AnonymousMessage(
            category=category,
            message=message_text,
            status='pending'
        )
        
        db.session.add(anonymous_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Your message has been submitted successfully. Thank you for your feedback!',
            'message_id': anonymous_msg.id
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting anonymous message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while submitting your message. Please try again.'
        }), 500


@anonymous_api_bp.route('/messages', methods=['GET'])
@login_required
def get_messages():
    """Get all anonymous messages (admin only)"""
    # Check if user is admin
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Unauthorized access'
        }), 403
    
    try:
        # Get filter parameters
        status = request.args.get('status', None)
        category = request.args.get('category', None)
        
        # Build query
        query = AnonymousMessage.query
        
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        # Order by newest first
        messages = query.order_by(AnonymousMessage.timestamp.desc()).all()
        
        # Convert to dict
        messages_data = [msg.to_dict() for msg in messages]
        
        return jsonify({
            'success': True,
            'messages': messages_data,
            'total': len(messages_data)
        })
    
    except Exception as e:
        print(f"Error fetching anonymous messages: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching messages'
        }), 500


@anonymous_api_bp.route('/messages/<int:message_id>', methods=['PUT'])
@login_required
def update_message(message_id):
    """Update message status or add admin response (admin only)"""
    # Check if user is admin
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Unauthorized access'
        }), 403
    
    try:
        message = AnonymousMessage.query.get(message_id)
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        data = request.get_json()
        
        # Update status if provided
        if 'status' in data:
            valid_statuses = ['pending', 'reviewed', 'resolved']
            if data['status'] in valid_statuses:
                message.status = data['status']
                if data['status'] in ['reviewed', 'resolved']:
                    message.is_read = True
        
        # Update admin notes if provided
        if 'admin_response' in data or 'admin_notes' in data:
            message.admin_notes = data.get('admin_response') or data.get('admin_notes')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message updated successfully',
            'data': message.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating anonymous message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while updating the message'
        }), 500


@anonymous_api_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete an anonymous message (admin only)"""
    # Check if user is admin
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Unauthorized access'
        }), 403
    
    try:
        message = AnonymousMessage.query.get(message_id)
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting anonymous message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while deleting the message'
        }), 500
