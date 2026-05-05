"""
Visitor management service with facial recognition
Handles visitor check-in/out and returning visitor detection
"""

import cv2
import numpy as np
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Visitor face detection will be disabled.")
import pickle
from models import db
from models.visitor_entry import VisitorEntry
from datetime import datetime, timedelta


class VisitorService:
    """Service for managing visitor entries with facial recognition"""
    
    def __init__(self):
        self.known_visitor_faces = {}
        self._faces_loaded = False
        print("Visitor service initialized")
    
    def load_visitor_faces(self):
        """Load all visitor face encodings from database"""
        try:
            from flask import has_app_context
            if not has_app_context():
                print("Warning: No app context available for visitor faces")
                return
            
            # Load all visitors who have face encodings
            visitors = VisitorEntry.query.filter(
                VisitorEntry.face_encoding.isnot(None)
            ).all()
            
            loaded_count = 0
            for visitor in visitors:
                try:
                    encoding = pickle.loads(visitor.face_encoding)
                    # Use visitor ID as key
                    self.known_visitor_faces[visitor.id] = {
                        'encoding': encoding,
                        'name': visitor.name,
                        'visit_count': visitor.previous_visit_count
                    }
                    loaded_count += 1
                except Exception as e:
                    print(f"Error loading face encoding for visitor {visitor.id}: {e}")
            
            self._faces_loaded = True
            print(f"Loaded {loaded_count} visitor face encodings")
        except Exception as e:
            print(f"Error loading visitor faces: {e}")
    
    def _ensure_faces_loaded(self):
        """Ensure visitor faces are loaded"""
        if not self._faces_loaded:
            self.load_visitor_faces()
    
    def check_returning_visitor(self, image_data):
        """
        Check if visitor has visited before using face recognition
        Returns: (is_returning, visitor_data, confidence)
        """
        try:
            self._ensure_faces_loaded()
            
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return False, None, 0.0, "No face detected"
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return False, None, 0.0, "Could not encode face"
            
            face_encoding = face_encodings[0]
            
            # If no known visitors, this is a new visitor
            if len(self.known_visitor_faces) == 0:
                return False, None, 0.0, "No previous visitors in database"
            
            # Compare with all known visitor faces
            best_match_id = None
            best_match_distance = float('inf')
            
            for visitor_id, visitor_data in self.known_visitor_faces.items():
                known_encoding = visitor_data['encoding']
                distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                
                if distance < best_match_distance:
                    best_match_distance = distance
                    best_match_id = visitor_id
            
            # Threshold for visitor matching (slightly more lenient than user matching)
            VISITOR_MATCH_THRESHOLD = 0.55
            
            if best_match_distance < VISITOR_MATCH_THRESHOLD:
                # Returning visitor found!
                visitor = VisitorEntry.query.get(best_match_id)
                confidence = (1 - best_match_distance) * 100
                return True, visitor, confidence, "Returning visitor recognized"
            else:
                return False, None, 0.0, f"No match found (best distance: {best_match_distance:.2f})"
        
        except Exception as e:
            print(f"Error checking returning visitor: {e}")
            return False, None, 0.0, f"Error: {str(e)}"
    
    def check_if_student_or_faculty(self, image_data):
        """
        Check if the person in the image is a registered student or faculty member
        Returns: (is_member, user_data, confidence, message)
        """
        try:
            # Import face recognition service
            from services.face_recognition import face_recognition_service
            
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return False, None, 0.0, "No face detected"
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return False, None, 0.0, "Could not encode face"
            
            face_encoding = face_encodings[0]
            
            # Check against known student/faculty faces
            if len(face_recognition_service.known_faces) == 0:
                return False, None, 0.0, "No registered users in database"
            
            # Compare with all known faces
            best_match_user_id = None
            best_match_distance = float('inf')
            
            for user_id, user_data in face_recognition_service.known_faces.items():
                known_encoding = user_data['encoding']
                distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                
                if distance < best_match_distance:
                    best_match_distance = distance
                    best_match_user_id = user_id
            
            # Use same threshold as face recognition service
            FACE_MATCH_THRESHOLD = 0.5
            
            if best_match_distance < FACE_MATCH_THRESHOLD:
                # This person is a registered student/faculty!
                from models import User
                user = User.query.get(best_match_user_id)
                if user:
                    confidence = (1 - best_match_distance) * 100
                    return True, user, confidence, f"Recognized as {user.role}: {user.full_name}"
            
            return False, None, 0.0, "Not a registered student/faculty member"
        
        except Exception as e:
            print(f"Error checking if student/faculty: {e}")
            return False, None, 0.0, f"Error: {str(e)}"
    
    def create_visitor_entry(self, name, reason, image_data, phone=None, 
                           organization=None, host_name=None, created_by_role='kiosk'):
        """
        Create new visitor entry with face enrollment
        First checks if person is a registered student/faculty member
        Returns: (success, visitor_entry, message)
        """
        try:
            # CRITICAL: First check if this person is a registered student/faculty member
            is_member, user, confidence, check_message = self.check_if_student_or_faculty(image_data)
            
            if is_member and user:
                # Deny entry - this is a registered student/faculty member!
                return False, None, f"Access Denied: You are registered as {user.role} ({user.full_name}). Please use the student/faculty entry system, not the visitor kiosk."
            
            # Not a student/faculty member, proceed with visitor check-in
            # Check if this is a returning visitor
            is_returning, previous_visitor, confidence, check_message = self.check_returning_visitor(image_data)
            
            # Enroll face
            face_encoding = None
            try:
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_image)
                if len(face_locations) > 0:
                    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
                    if len(face_encodings) > 0:
                        face_encoding = pickle.dumps(face_encodings[0])
            except Exception as e:
                print(f"Warning: Could not enroll face: {e}")
            
            # Calculate previous visit count
            previous_visit_count = 0
            if is_returning and previous_visitor:
                previous_visit_count = previous_visitor.previous_visit_count + 1
            
            # Create visitor entry
            visitor_entry = VisitorEntry(
                name=name,
                reason=reason,
                phone=phone,
                organization=organization,
                host_name=host_name,
                photo=image_data,
                face_encoding=face_encoding,
                status='IN',
                is_returning_visitor=is_returning,
                previous_visit_count=previous_visit_count,
                created_by_role=created_by_role
            )
            
            db.session.add(visitor_entry)
            db.session.commit()
            
            # Update known faces cache
            if face_encoding:
                self.known_visitor_faces[visitor_entry.id] = {
                    'encoding': pickle.loads(face_encoding),
                    'name': name,
                    'visit_count': previous_visit_count
                }
            
            if is_returning:
                message = f"Welcome back, {name}! This is visit #{previous_visit_count + 1}"
            else:
                message = f"Welcome, {name}! First time visitor"
            
            return True, visitor_entry, message
        
        except Exception as e:
            print(f"Error creating visitor entry: {e}")
            db.session.rollback()
            return False, None, f"Error: {str(e)}"
    
    def mark_visitor_exit(self, visitor_id):
        """Mark visitor as exited"""
        try:
            visitor = VisitorEntry.query.get(visitor_id)
            if not visitor:
                return False, "Visitor not found"
            
            if visitor.status == 'OUT':
                return False, "Visitor already checked out"
            
            visitor.exit_time = datetime.utcnow()
            visitor.status = 'OUT'
            db.session.commit()
            
            return True, f"{visitor.name} checked out successfully"
        
        except Exception as e:
            print(f"Error marking visitor exit: {e}")
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    def get_active_visitors(self):
        """Get all currently checked-in visitors"""
        try:
            visitors = VisitorEntry.query.filter_by(status='IN').order_by(
                VisitorEntry.entry_time.desc()
            ).all()
            return visitors
        except Exception as e:
            print(f"Error getting active visitors: {e}")
            return []
    
    def get_visitor_history(self, days=30):
        """Get visitor history for the past N days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            visitors = VisitorEntry.query.filter(
                VisitorEntry.entry_time >= start_date
            ).order_by(VisitorEntry.entry_time.desc()).all()
            return visitors
        except Exception as e:
            print(f"Error getting visitor history: {e}")
            return []
    
    def search_visitors(self, query):
        """Search visitors by name"""
        try:
            visitors = VisitorEntry.query.filter(
                VisitorEntry.name.ilike(f'%{query}%')
            ).order_by(VisitorEntry.entry_time.desc()).limit(50).all()
            return visitors
        except Exception as e:
            print(f"Error searching visitors: {e}")
            return []
    
    def get_visitor_stats(self, days=30):
        """Get visitor statistics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            total_visitors = VisitorEntry.query.filter(
                VisitorEntry.entry_time >= start_date
            ).count()
            
            active_visitors = VisitorEntry.query.filter_by(status='IN').count()
            
            returning_visitors = VisitorEntry.query.filter(
                VisitorEntry.entry_time >= start_date,
                VisitorEntry.is_returning_visitor == True
            ).count()
            
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_visitors = VisitorEntry.query.filter(
                VisitorEntry.entry_time >= today_start
            ).count()
            
            return {
                'total_visitors': total_visitors,
                'active_visitors': active_visitors,
                'returning_visitors': returning_visitors,
                'today_visitors': today_visitors
            }
        except Exception as e:
            print(f"Error getting visitor stats: {e}")
            return {
                'total_visitors': 0,
                'active_visitors': 0,
                'returning_visitors': 0,
                'today_visitors': 0
            }


# Global visitor service instance
visitor_service = VisitorService()
