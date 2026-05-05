"""
Emotion Detection API Routes
Provides endpoints for analyzing facial emotions
"""

from flask import Blueprint, request, jsonify
from services.emotion_detection import emotion_service
import base64
import os
from werkzeug.utils import secure_filename

emotion_api_bp = Blueprint('emotion_api', __name__)


@emotion_api_bp.route('/analyze', methods=['POST'])
def analyze_emotion():
    """
    Analyze emotion from uploaded image
    
    Expects:
        - image: file upload or base64 encoded image
        
    Returns:
        JSON with emotion analysis results
    """
    try:
        # Check if image is provided as file upload
        if 'image' in request.files:
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Save temporarily
            temp_path = os.path.join('/tmp', secure_filename(file.filename))
            file.save(temp_path)
            
            # Analyze emotion
            result = emotion_service.analyze_from_file(temp_path)
            
            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass
            
            return jsonify(result)
        
        # Check if image is provided as base64
        elif request.json and 'image' in request.json:
            base64_image = request.json['image']
            result = emotion_service.analyze_from_base64(base64_image)
            return jsonify(result)
        
        else:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'dominant_emotion': 'neutral',
            'greeting_message': ''
        }), 500


@emotion_api_bp.route('/health', methods=['GET'])
def health_check():
    """Check if emotion detection service is available"""
    return jsonify({
        'status': 'ok',
        'service': 'emotion_detection',
        'initialized': emotion_service.initialized
    })
