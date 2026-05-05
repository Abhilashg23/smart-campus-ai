from flask import Blueprint, request, jsonify, send_file
from flask_login import current_user
from services.voice_chat import voice_chat_service
import io

voice_api_bp = Blueprint('voice_api', __name__)


@voice_api_bp.route('/process', methods=['POST'])
def process():
    """Process voice input and return voice response"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400
    
    audio_file = request.files['audio']
    audio_data = audio_file.read()
    
    # Get user info if logged in
    user_id = current_user.id if current_user.is_authenticated else None
    user_role = current_user.role if current_user.is_authenticated else None
    
    # Process voice query
    success, user_message, response_text, audio_or_error = voice_chat_service.process_voice_query(
        audio_data,
        user_id,
        user_role
    )
    
    if success:
        # Return audio response
        return send_file(
            io.BytesIO(audio_or_error),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='response.mp3'
        )
    else:
        return jsonify({
            'success': False,
            'error': audio_or_error,
            'user_message': user_message,
            'response_text': response_text
        }), 400


@voice_api_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    success, audio_or_error = voice_chat_service.text_to_speech(text)
    
    if success:
        return send_file(
            io.BytesIO(audio_or_error),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
    else:
        return jsonify({
            'success': False,
            'error': audio_or_error
        }), 400
