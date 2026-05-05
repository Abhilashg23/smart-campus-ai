from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from services.chatbot import chatbot
from services.face_recognition import face_recognition_service
from models import db, User, StudentTracking
from datetime import datetime, timedelta
import pytz

chat_api_bp = Blueprint('chat_api', __name__)


@chat_api_bp.route('/', methods=['POST'])
def chat():
    """Chat API endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get user info if logged in
    user_id = current_user.id if current_user.is_authenticated else None
    user_role = current_user.role if current_user.is_authenticated else None
    
    # Get chatbot response (now returns a dictionary)
    response_data = chatbot.get_response(message, user_id, user_role)
    
    # Build JSON response
    json_response = {
        'message': message,
        'response': response_data['response']
    }
    
    # Include image URL if available
    if response_data.get('image_url'):
        json_response['image_url'] = response_data['image_url']
    
    return jsonify(json_response)


@chat_api_bp.route('/history', methods=['GET'])
@login_required
def history():
    """Get chat history"""
    from models import ChatHistory
    
    history = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.desc()).limit(50).all()
    
    history_data = []
    for chat in history:
        history_data.append({
            'message': chat.message,
            'response': chat.response,
            'timestamp': chat.timestamp.isoformat(),
            'chat_type': chat.chat_type
        })
    
    return jsonify({'history': history_data})


@chat_api_bp.route('/recognize-image', methods=['POST'])
def recognize_image():
    """Recognize face in uploaded image and return user information"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No image file selected'
            }), 400
        
        # Read image data
        image_data = image_file.read()
        
        # Use face recognition service to identify the person
        success, user, message, emotion_result = face_recognition_service.verify_face(
            image_data,
            user_id=None,
            mark_attendance=False  # Don't mark attendance for image uploads
        )
        
        if success and user:
            # Get user's availability status
            ist = pytz.timezone('Asia/Kolkata')
            today_start = datetime.now(ist).replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # Get today's tracking records
            tracking_records = StudentTracking.query.filter(
                StudentTracking.user_id == user.id,
                StudentTracking.timestamp >= today_start,
                StudentTracking.timestamp < today_end
            ).order_by(StudentTracking.timestamp.desc()).all()
            
            # Determine current status
            availability_status = "Not entered today"
            last_entry_time = None
            
            if tracking_records:
                last_record = tracking_records[0]
                last_entry_time = last_record.timestamp.astimezone(ist).strftime('%I:%M %p')
                
                if last_record.entry_type == 'IN':
                    availability_status = f"Currently in university (entered at {last_entry_time})"
                else:
                    availability_status = f"Left university (last exit at {last_entry_time})"
            
            # Get department name if available
            department_name = user.department.name if user.department else "Not assigned"
            
            # Format user information
            user_info = {
                'success': True,
                'recognized': True,
                'user': {
                    'full_name': user.full_name,
                    'role': user.role,
                    'email': user.email,
                    'department': department_name,
                    'program': user.program.name if hasattr(user, 'program') and user.program else "N/A",
                    'availability': availability_status
                },
                'message': f"✅ Recognized: {user.full_name}"
            }
            
            return jsonify(user_info)
        else:
            # Face not recognized
            return jsonify({
                'success': True,
                'recognized': False,
                'message': '❌ Face not recognized. This person is not in our university database.'
            })
    
    except Exception as e:
        print(f"Error in recognize-image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500
