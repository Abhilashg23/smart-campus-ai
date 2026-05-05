import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from services.chatbot import chatbot
from models import db, ChatHistory


class VoiceChatService:
    """Voice-to-voice chat service"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def speech_to_text(self, audio_data):
        """Convert speech to text"""
        try:
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Load audio file
            with sr.AudioFile(temp_audio_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            return True, text
        
        except sr.UnknownValueError:
            return False, "Could not understand audio"
        except sr.RequestError as e:
            return False, f"Could not request results; {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def text_to_speech(self, text, language='en'):
        """Convert text to speech"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio_path = temp_audio.name
            
            tts.save(temp_audio_path)
            
            # Read audio file
            with open(temp_audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            return True, audio_data
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def process_voice_query(self, audio_data, user_id=None, user_role=None):
        """Process voice query end-to-end"""
        # Convert speech to text
        success, text_or_error = self.speech_to_text(audio_data)
        
        if not success:
            return False, None, None, text_or_error
        
        user_message = text_or_error
        
        # Get chatbot response
        response_text = chatbot.get_response(user_message, user_id, user_role)
        
        # If user is logged in, update chat history to mark as voice
        if user_id:
            last_chat = ChatHistory.query.filter_by(user_id=user_id).order_by(
                ChatHistory.timestamp.desc()
            ).first()
            if last_chat:
                last_chat.chat_type = 'voice'
                db.session.commit()
        
        # Convert response to speech
        success, audio_or_error = self.text_to_speech(response_text)
        
        if not success:
            return False, user_message, response_text, audio_or_error
        
        return True, user_message, response_text, audio_or_error


# Global voice chat instance
voice_chat_service = VoiceChatService()
