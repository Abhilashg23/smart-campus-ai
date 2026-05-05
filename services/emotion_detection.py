"""
Emotion Detection Service using DeepFace
Analyzes facial expressions and provides emotion data for personalized greetings
"""

import cv2
import numpy as np
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("Warning: deepface library not available. Emotion detection features will be disabled.")
import base64
from io import BytesIO
from PIL import Image


class EmotionDetectionService:
    """Service for detecting emotions and analyzing facial expressions"""
    
    def __init__(self):
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.initialized = False
        
    def initialize(self):
        """Initialize the emotion detection model"""
        try:
            # DeepFace will download models on first use
            print("Emotion Detection Service initialized")
            self.initialized = True
            return True
        except Exception as e:
            print(f"Error initializing emotion detection: {str(e)}")
            return False
    
    def analyze_emotion(self, image_data):
        """
        Analyze emotion from image data
        
        Args:
            image_data: Image as numpy array, PIL Image, or file path
            
        Returns:
            dict: {
                'success': bool,
                'dominant_emotion': str,
                'emotions': dict,
                'age': int,
                'gender': str,
                'confidence': float,
                'greeting_message': str
            }
        """
        try:
            if not DEEPFACE_AVAILABLE:
                return {
                    'success': False,
                    'error': 'DeepFace library not installed',
                    'dominant_emotion': 'neutral',
                    'emotions': {},
                    'greeting_message': ''
                }
            # Analyze the image using DeepFace
            analysis = DeepFace.analyze(
                img_path=image_data,
                actions=['emotion', 'age', 'gender'],
                enforce_detection=False,  # Don't fail if face not detected
                detector_backend='opencv'  # Fast detector
            )
            
            # Handle both single face and multiple faces
            if isinstance(analysis, list):
                analysis = analysis[0]  # Take first face
            
            # Extract emotion data
            emotions = analysis.get('emotion', {})
            dominant_emotion = analysis.get('dominant_emotion', 'neutral')
            age = analysis.get('age', 25)
            gender = analysis.get('dominant_gender', 'Unknown')
            
            # Calculate confidence (highest emotion score)
            confidence = max(emotions.values()) / 100.0 if emotions else 0.5
            
            # Generate greeting message based on emotion
            greeting_message = self._generate_greeting_message(
                dominant_emotion, 
                confidence,
                gender
            )
            
            return {
                'success': True,
                'dominant_emotion': dominant_emotion,
                'emotions': emotions,
                'age': int(age),
                'gender': gender,
                'confidence': confidence,
                'greeting_message': greeting_message
            }
            
        except Exception as e:
            print(f"Error analyzing emotion: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dominant_emotion': 'neutral',
                'emotions': {},
                'greeting_message': ''
            }
    
    def _generate_greeting_message(self, emotion, confidence, gender):
        """Generate personalized greeting based on emotion"""
        
        # Only add emotion-based message if confidence is high enough
        if confidence < 0.6:
            return ""
        
        messages = {
            'happy': [
                "You're looking great today!",
                "Your smile brightens the campus!",
                "What a wonderful energy you bring!",
                "You seem to be in a great mood!"
            ],
            'sad': [
                "I hope I can brighten your day!",
                "I'm here to help make your day better!",
                "I hope your day gets better!"
            ],
            'surprise': [
                "You look surprised!",
                "Something exciting happening today?",
            ],
            'neutral': [
                "",  # No additional message for neutral
            ],
            'angry': [
                "I'm here to help.",
            ],
            'fear': [
                "Don't worry, I'm here to help!",
            ]
        }
        
        # Get appropriate message for the emotion
        emotion_messages = messages.get(emotion, messages['neutral'])
        
        # Return first message (can be randomized later)
        return emotion_messages[0] if emotion_messages else ""
    
    def analyze_from_base64(self, base64_image):
        """Analyze emotion from base64 encoded image"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image.split(',')[1] if ',' in base64_image else base64_image)
            image = Image.open(BytesIO(image_data))
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return self.analyze_emotion(img_array)
            
        except Exception as e:
            print(f"Error processing base64 image: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dominant_emotion': 'neutral',
                'emotions': {},
                'greeting_message': ''
            }
    
    def analyze_from_file(self, file_path):
        """Analyze emotion from image file"""
        try:
            return self.analyze_emotion(file_path)
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'dominant_emotion': 'neutral',
                'emotions': {},
                'greeting_message': ''
            }


# Global emotion detection service instance
emotion_service = EmotionDetectionService()
