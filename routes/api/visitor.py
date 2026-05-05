"""
API endpoints for visitor management
Handles check-in, check-out, and visitor queries
"""

from flask import Blueprint, request, jsonify, send_file
from services.visitor_service import visitor_service
from services.voice_guidance import voice_guidance
from io import BytesIO
import base64

visitor_api_bp = Blueprint('visitor_api', __name__)


@visitor_api_bp.route('/check-in', methods=['POST'])
def check_in():
    """Check in a visitor with photo"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        
        if not data.get('reason'):
            return jsonify({'success': False, 'message': 'Reason is required'}), 400
        
        if not data.get('photo'):
            return jsonify({'success': False, 'message': 'Photo is required'}), 400
        
        # Decode base64 image
        try:
            photo_data = base64.b64decode(data['photo'].split(',')[1] if ',' in data['photo'] else data['photo'])
        except Exception as e:
            return jsonify({'success': False, 'message': f'Invalid photo format: {str(e)}'}), 400
        
        # Create visitor entry
        success, visitor_entry, message = visitor_service.create_visitor_entry(
            name=data['name'],
            reason=data['reason'],
            image_data=photo_data,
            phone=data.get('phone'),
            organization=data.get('organization'),
            host_name=data.get('host_name'),
            created_by_role=data.get('created_by_role', 'kiosk')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'visitor': visitor_entry.to_dict(),
                'is_returning': visitor_entry.is_returning_visitor,
                'visit_count': visitor_entry.previous_visit_count + 1
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
    
    except Exception as e:
        print(f"Check-in error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/check-out', methods=['POST'])
def check_out():
    """Check out a visitor"""
    try:
        data = request.get_json()
        
        if not data.get('visitor_id'):
            return jsonify({'success': False, 'message': 'Visitor ID is required'}), 400
        
        success, message = visitor_service.mark_visitor_exit(data['visitor_id'])
        
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        print(f"Check-out error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/recognize', methods=['POST'])
def recognize():
    """Recognize returning visitor from photo"""
    try:
        data = request.get_json()
        
        if not data.get('photo'):
            return jsonify({'success': False, 'message': 'Photo is required'}), 400
        
        # Decode base64 image
        try:
            photo_data = base64.b64decode(data['photo'].split(',')[1] if ',' in data['photo'] else data['photo'])
        except Exception as e:
            return jsonify({'success': False, 'message': f'Invalid photo format: {str(e)}'}), 400
        
        # Check for returning visitor
        is_returning, visitor, confidence, message = visitor_service.check_returning_visitor(photo_data)
        
        if is_returning and visitor:
            return jsonify({
                'success': True,
                'is_returning': True,
                'visitor': visitor.to_dict(),
                'confidence': confidence,
                'message': f'Welcome back, {visitor.name}!'
            })
        else:
            return jsonify({
                'success': True,
                'is_returning': False,
                'message': 'New visitor'
            })
    
    except Exception as e:
        print(f"Recognition error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/active', methods=['GET'])
def get_active():
    """Get all active (checked-in) visitors"""
    try:
        visitors = visitor_service.get_active_visitors()
        return jsonify({
            'success': True,
            'visitors': [v.to_dict() for v in visitors],
            'count': len(visitors)
        })
    except Exception as e:
        print(f"Get active visitors error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/history', methods=['GET'])
def get_history():
    """Get visitor history"""
    try:
        days = request.args.get('days', 30, type=int)
        visitors = visitor_service.get_visitor_history(days)
        
        return jsonify({
            'success': True,
            'visitors': [v.to_dict() for v in visitors],
            'count': len(visitors)
        })
    except Exception as e:
        print(f"Get history error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/search', methods=['GET'])
def search():
    """Search visitors by name"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'success': False, 'message': 'Search query is required'}), 400
        
        visitors = visitor_service.search_visitors(query)
        
        return jsonify({
            'success': True,
            'visitors': [v.to_dict() for v in visitors],
            'count': len(visitors)
        })
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get visitor statistics"""
    try:
        days = request.args.get('days', 30, type=int)
        stats = visitor_service.get_visitor_stats(days)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Get stats error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/photo/<int:visitor_id>', methods=['GET'])
def get_photo(visitor_id):
    """Get visitor photo"""
    try:
        from models.visitor_entry import VisitorEntry
        
        visitor = VisitorEntry.query.get(visitor_id)
        if not visitor or not visitor.photo:
            return jsonify({'success': False, 'message': 'Photo not found'}), 404
        
        return send_file(
            BytesIO(visitor.photo),
            mimetype='image/jpeg',
            as_attachment=False
        )
    except Exception as e:
        print(f"Get photo error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@visitor_api_bp.route('/voice-prompts', methods=['GET'])
def get_voice_prompts():
    """Get all voice guidance prompts"""
    try:
        prompts = voice_guidance.get_all_prompts()
        return jsonify({
            'success': True,
            'prompts': prompts
        })
    except Exception as e:
        print(f"Get voice prompts error: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
