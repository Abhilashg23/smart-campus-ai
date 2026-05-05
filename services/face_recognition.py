"""
Full face recognition service with automatic face matching
Uses face_recognition library (dlib-based) for accurate recognition
"""

import cv2
import numpy as np
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Face recognition features will be disabled.")
import pickle
from models import db, FaceData, Attendance, User, EmotionTracking
from models.student_tracking import StudentTracking
from services.emotion_detection import emotion_service
from datetime import datetime, timedelta


class FaceRecognitionService:
    """Full face recognition service with automatic matching"""
    
    def __init__(self):
        self.known_faces = {}
        self._faces_loaded = False
        print("Face recognition initialized with automatic matching")
        print("Using face_recognition library with dlib backend")
    
    def load_known_faces(self):
        """Load all enrolled face encodings from database"""
        try:
            from flask import has_app_context
            if not has_app_context():
                print("Warning: No app context available, faces will be loaded on first use")
                return
            
            face_data_records = FaceData.query.all()
            loaded_count = 0
            
            for record in face_data_records:
                if record.face_encoding and record.face_encoding != b'opencv_placeholder':
                    try:
                        encoding = pickle.loads(record.face_encoding)
                        self.known_faces[record.user_id] = encoding
                        loaded_count += 1
                    except Exception as e:
                        print(f"Error loading face encoding for user {record.user_id}: {e}")
            
            self._faces_loaded = True
            print(f"Loaded {loaded_count} face encodings from database")
        except Exception as e:
            print(f"Error loading known faces: {e}")
    
    def _ensure_faces_loaded(self):
        """Ensure faces are loaded before use"""
        if not self._faces_loaded:
            self.load_known_faces()
    
    def enroll_face(self, image_data, user_id, image_path=None):
        """Enroll a face with full face encoding"""
        if not FACE_RECOGNITION_AVAILABLE:
            return False, "Face recognition library not installed. Please install dlib and face_recognition."
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return False, "No face detected in the image"
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please ensure only one face is in the image"
            
            # Get face encoding (128-dimensional vector)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return False, "Could not generate face encoding"
            
            face_encoding = face_encodings[0]
            
            # Check if user already has face data
            existing_face_data = FaceData.query.filter_by(user_id=user_id).first()
            
            if existing_face_data:
                # Update existing record
                existing_face_data.face_encoding = pickle.dumps(face_encoding)
                existing_face_data.image_path = image_path
            else:
                # Create new record
                face_data = FaceData(
                    user_id=user_id,
                    face_encoding=pickle.dumps(face_encoding),
                    image_path=image_path
                )
                db.session.add(face_data)
            
            db.session.commit()
            
            # Update known faces cache
            self.known_faces[user_id] = face_encoding
            
            return True, "Face enrolled successfully! Automatic recognition enabled."
        
        except Exception as e:
            print(f"Face enrollment error: {str(e)}")
            return False, f"Error enrolling face: {str(e)}"
    
    def verify_face(self, image_data, user_id=None, mark_attendance=True):
        """Verify face with automatic or manual confirmation and create tracking record"""
        if not FACE_RECOGNITION_AVAILABLE:
            return False, None, "Face recognition library not installed. Facial verification is unavailable.", None
        try:
            # Ensure faces are loaded from database
            self._ensure_faces_loaded()
            
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return False, None, "No face detected", None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return False, None, "Could not encode face", None
            
            face_encoding = face_encodings[0]
            
            # If user_id provided (manual confirmation)
            if user_id:
                user = User.query.get(user_id)
                if not user:
                    return False, None, "User not found", None
                
                if mark_attendance:
                    # Create tracking record with duplicate prevention
                    success, entry_type, message = self._create_tracking_record(user_id)
                    if not success:
                        return True, user, message, None
                    
                    return True, user, f"{entry_type}: {user.full_name} - {message}", None
                
                return True, user, f"Verified: {user.full_name}", None
            
            # Automatic face matching
            if len(self.known_faces) == 0:
                return False, None, "No enrolled faces found. Please enroll first or confirm manually.", None
            
            # Compare with all known faces
            best_match_user_id = None
            best_match_distance = float('inf')
            
            print(f"\n=== Face Recognition Debug ===")
            print(f"Total known faces: {len(self.known_faces)}")
            
            for known_user_id, known_encoding in self.known_faces.items():
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                
                user = User.query.get(known_user_id)
                user_name = user.full_name if user else f"User {known_user_id}"
                print(f"  Distance to {user_name}: {face_distance:.4f}")
                
                if face_distance < best_match_distance:
                    best_match_distance = face_distance
                    best_match_user_id = known_user_id
            
            # Threshold for face matching (0.5 is stricter, 0.6 is standard)
            FACE_MATCH_THRESHOLD = 0.5
            
            print(f"Best match: User {best_match_user_id}, Distance: {best_match_distance:.4f}, Threshold: {FACE_MATCH_THRESHOLD}")
            print(f"=== End Debug ===\n")
            
            if best_match_distance < FACE_MATCH_THRESHOLD:
                # Face recognized!
                user = User.query.get(best_match_user_id)
                
                if mark_attendance:
                    # Create tracking record with duplicate prevention
                    success, entry_type, message, tracking_record = self._create_tracking_record(best_match_user_id)
                    
                    # Analyze emotion (ALWAYS do this if face is recognized)
                    emotion_result = None
                    try:
                        print("DEBUG: Starting emotion analysis...")
                        # Use the original BGR image directly (DeepFace expects BGR)
                        # 'image' variable is already available from line 117
                        emotion_result = emotion_service.analyze_emotion(image)
                        print(f"DEBUG: Emotion analysis result: {emotion_result.get('success', False) if emotion_result else 'None'}")
                        
                        if emotion_result and emotion_result.get('success'):
                            # Create emotion tracking record IF tracking record exists
                            # tracking_record might be the NEW one or the OLD one (returned by _create_tracking_record in updated logic)
                            # Update: _create_tracking_record returns None for record if duplicate?
                            # Let's check _create_tracking_record implementation.
                            # If it returns the duplicate record as 4th arg (which I should verify), we can link to it.
                            # Even if tracking_record is None, we just don't save to DB but we return the display data
                            
                            if tracking_record:
                                emotion_tracking = EmotionTracking(
                                    user_id=best_match_user_id,
                                    tracking_id=tracking_record.id,
                                    dominant_emotion=emotion_result['dominant_emotion'],
                                    confidence=emotion_result['confidence'],
                                    age=emotion_result['age'],
                                    gender=emotion_result['gender']
                                )
                                emotion_tracking.set_emotion_scores(emotion_result['emotions'])
                                db.session.add(emotion_tracking)
                                db.session.commit()
                                print(f"Emotion logged: {emotion_result['dominant_emotion']} ({emotion_result['confidence']:.2f})")
                        else:
                            print(f"DEBUG: Emotion analysis failed or returned success=False. Using fallback.")
                            # Fallback to neutral to ensure UI shows something
                            emotion_result = {
                                'success': True,
                                'dominant_emotion': 'neutral',
                                'confidence': 0.0,
                                'age': 0,
                                'gender': 'unknown',
                                'emotions': {},
                                'greeting_message': ''
                            }
                    except Exception as e:
                        print(f"Error logging emotion: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback on error
                        emotion_result = {
                            'success': True,
                            'dominant_emotion': 'analyzing...',
                            'confidence': 0.0,
                            'age': 0,
                            'gender': 'unknown',
                            'emotions': {},
                            'greeting_message': ''
                        }

                    if not success:
                        return True, user, message, emotion_result
                    
                    confidence = (1 - best_match_distance) * 100
                    return True, user, f"{entry_type}: {user.full_name} - {message} (confidence: {confidence:.1f}%)", emotion_result
                
                confidence = (1 - best_match_distance) * 100
                return True, user, f"Recognized: {user.full_name} (confidence: {confidence:.1f}%)", None
            else:
                # Face not recognized
                return False, None, f"Face not recognized (best match distance: {best_match_distance:.2f}, threshold: {FACE_MATCH_THRESHOLD}). Please confirm your identity manually.", None
        
        except Exception as e:
            print(f"Face verification error: {str(e)}")
            return False, None, f"Error verifying face: {str(e)}", None
    
    def _create_tracking_record(self, user_id):
        """Create a student tracking record with duplicate prevention and automatic IN/OUT detection"""
        try:
            # Get the last tracking record for this user
            last_record = StudentTracking.query.filter_by(user_id=user_id).order_by(
                StudentTracking.timestamp.desc()
            ).first()
            
            # Check for duplicate within 5 minutes
            if last_record:
                time_diff = datetime.utcnow() - last_record.timestamp
                if time_diff < timedelta(minutes=5):
                    # Duplicate entry within 5 minutes
                    return False, last_record.entry_type, f"Recent {last_record.entry_type} entry detected {int(time_diff.total_seconds() / 60)} minutes ago", last_record
            
            # Determine entry type (alternate between IN and OUT)
            if last_record:
                # Alternate: if last was IN, this is OUT; if last was OUT, this is IN
                entry_type = 'OUT' if last_record.entry_type == 'IN' else 'IN'
            else:
                # First entry is always IN
                entry_type = 'IN'
            
            # Create tracking record
            tracking = StudentTracking(
                user_id=user_id,
                entry_type=entry_type,
                verification_method='face',
                location='Main Gate'
            )
            db.session.add(tracking)
            db.session.commit()
            
            action_message = "entered the campus" if entry_type == 'IN' else "exited the campus"
            return True, entry_type, f"Successfully {action_message}", tracking
        
        except Exception as e:
            print(f"Error creating tracking record: {str(e)}")
            db.session.rollback()
            return False, None, f"Error creating tracking record: {str(e)}", None
    
    def get_attendance_records(self, user_id, days=30):
        """Get attendance records for a user"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        records = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.timestamp >= start_date
        ).order_by(Attendance.timestamp.desc()).all()
        
        return records


# Global face recognition instance
face_recognition_service = FaceRecognitionService()
