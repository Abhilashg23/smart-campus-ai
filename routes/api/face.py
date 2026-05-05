from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from services.face_recognition import face_recognition_service
from utils.helpers import save_uploaded_file
from flask import current_app
import os

face_api_bp = Blueprint('face_api', __name__)


@face_api_bp.route('/enroll', methods=['POST'])
@login_required
def enroll():
    """Enroll face for current user"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    
    # Save image
    image_path = save_uploaded_file(
        image_file,
        current_app.config['FACE_DATA_FOLDER'],
        current_app.config['ALLOWED_EXTENSIONS']
    )
    
    # Read image data
    image_file.seek(0)
    image_data = image_file.read()
    
    # Enroll face
    success, message = face_recognition_service.enroll_face(
        image_data,
        current_user.id,
        image_path
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        # Clean up saved image if enrollment failed
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({
            'success': False,
            'error': message
        }), 400


@face_api_bp.route('/verify', methods=['POST'])
def verify():
    """Verify face and mark attendance"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    image_data = image_file.read()
    
    # Get user_id from form data (for manual confirmation)
    user_id = request.form.get('user_id')
    
    # Verify face
    # Verify face
    success, user, message, emotion_data = face_recognition_service.verify_face(
        image_data,
        user_id=int(user_id) if user_id else None,
        mark_attendance=True
    )
    
    if success:
        response_data = {
            'success': True,
            'message': message,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'registration_id': getattr(user, 'registration_id', ''),
                'role': user.role
            }
        }
        
        # Add emotion data if available
        if emotion_data:
            response_data['emotion'] = {
                'dominant_emotion': emotion_data.get('dominant_emotion'),
                'confidence': emotion_data.get('confidence'),
                'greeting_message': emotion_data.get('greeting_message')
            }
            
        return jsonify(response_data)
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400




@face_api_bp.route('/recognize-visitor', methods=['POST'])
def recognize_visitor():
    """Recognize face for visitor display (no attendance marking, no login required)"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided', 'success': False, 'face_detected': False}), 400
    
    image_file = request.files['image']
    image_data = image_file.read()
    
    # First, check if there's actually a face in the image
    import numpy as np
    import cv2
    import face_recognition as fr
    
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({
                'success': False,
                'recognized': False,
                'face_detected': False,
                'message': 'Invalid image data'
            })
        
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces first
        face_locations = fr.face_locations(rgb_img)
        
        # If no faces detected, return immediately
        if len(face_locations) == 0:
            return jsonify({
                'success': False,
                'recognized': False,
                'face_detected': False,
                'message': 'No face detected in frame'
            })
        
        # Face detected, now try to recognize
        success, user, message, _ = face_recognition_service.verify_face(
            image_data,
            user_id=None,
            mark_attendance=False  # Don't mark attendance for visitor page
        )
        
        # Analyze emotion if face is detected
        emotion_data = None
        try:
            from services.emotion_detection import emotion_service
            
            # Analyze emotion
            emotion_result = emotion_service.analyze_emotion(img)
            if emotion_result.get('success'):
                emotion_data = {
                    'emotion': emotion_result.get('dominant_emotion', 'neutral'),
                    'confidence': emotion_result.get('confidence', 0.5),
                    'greeting_message': emotion_result.get('greeting_message', ''),
                    'age': emotion_result.get('age'),
                    'gender': emotion_result.get('gender')
                }
        except Exception as e:
            print(f"Error analyzing emotion: {str(e)}")
            # Continue without emotion data
        
        if success and user:
            return jsonify({
                'success': True,
                'recognized': True,
                'face_detected': True,
                'message': message,
                'user': {
                    'id': user.id,
                    'full_name': user.full_name,
                    'first_name': getattr(user, 'first_name', user.full_name.split()[0] if user.full_name else ''),
                    'role': user.role
                },
                'emotion': emotion_data
            })
        else:
            # Face detected but not recognized - guest visitor
            return jsonify({
                'success': True,
                'recognized': False,
                'face_detected': True,
                'message': 'Face detected but not recognized - guest visitor',
                'emotion': emotion_data
            })
    
    except Exception as e:
        print(f"Error in recognize-visitor: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'recognized': False,
            'face_detected': False,
            'message': f'Error processing image: {str(e)}'
        })


@face_api_bp.route('/attendance/<int:user_id>', methods=['GET'])
@login_required
def attendance(user_id):
    """Get attendance records for a user"""
    # Only allow users to view their own attendance or admins to view any
    if current_user.id != user_id and current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    days = request.args.get('days', 30, type=int)
    records = face_recognition_service.get_attendance_records(user_id, days)
    
    attendance_data = []
    for record in records:
        attendance_data.append({
            'timestamp': record.timestamp.isoformat(),
            'status': record.status,
            'verification_method': record.verification_method,
            'location': record.location
        })
    
    return jsonify({'attendance': attendance_data})

