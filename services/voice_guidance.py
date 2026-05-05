"""
Voice guidance service for visitor kiosk
Provides text-to-speech prompts for each step
"""


class VoiceGuidanceService:
    """Service for generating voice guidance prompts"""
    
    def __init__(self):
        self.prompts = {
            'welcome': "Welcome to the Smart Campus Visitor Kiosk. Please follow the on-screen instructions.",
            'enter_name': "Please enter your full name.",
            'enter_reason': "Please tell us the reason for your visit.",
            'enter_phone': "Please enter your phone number. This is optional.",
            'enter_organization': "Please enter your organization or company name. This is optional.",
            'enter_host': "Who are you here to meet? This is optional.",
            'capture_photo': "Please look at the camera. We will capture your photo in 3, 2, 1.",
            'photo_captured': "Photo captured successfully.",
            'processing': "Processing your information. Please wait.",
            'returning_visitor': "Welcome back! We recognize you as a returning visitor.",
            'new_visitor': "Welcome! This is your first visit to our campus.",
            'success': "Check-in successful. Enjoy your visit!",
            'error': "An error occurred. Please try again or contact the reception desk.",
            'checkout_success': "Check-out successful. Thank you for visiting!",
            'no_face_detected': "No face detected. Please position yourself in front of the camera.",
            'multiple_faces': "Multiple faces detected. Please ensure only one person is in front of the camera."
        }
    
    def get_prompt(self, key):
        """Get voice prompt by key"""
        return self.prompts.get(key, "")
    
    def get_all_prompts(self):
        """Get all prompts for client-side caching"""
        return self.prompts


# Global voice guidance instance
voice_guidance = VoiceGuidanceService()
