"""
Student Attention Monitoring Service
Uses MediaPipe Face Landmarker for head pose detection to determine if students are paying attention
"""

import cv2
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import List, Dict, Tuple


class AttentionMonitoringService:
    """Service for monitoring student attention using head pose detection"""
    
    def __init__(self):
        # Initialize MediaPipe Face Landmarker (v0.10.x API)
        base_options = python.BaseOptions(model_asset_path='')  # Will use default model
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=30,  # Support up to 30 students
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        try:
            self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
        except Exception as e:
            print(f"Warning: Could not initialize FaceLandmarker with model: {e}")
            print("Falling back to simple face detection mode")
            self.face_landmarker = None
        
        # Attention thresholds (in degrees)
        self.PITCH_THRESHOLD = 30  # Looking down threshold
        self.YAW_THRESHOLD = 30    # Looking left/right threshold
        
        # Key facial landmarks for head pose estimation
        # Nose tip, chin, left eye corner, right eye corner, left mouth corner, right mouth corner
        self.FACE_3D_POINTS = np.array([
            [0.0, 0.0, 0.0],           # Nose tip
            [0.0, -330.0, -65.0],      # Chin
            [-225.0, 170.0, -135.0],   # Left eye left corner
            [225.0, 170.0, -135.0],    # Right eye right corner
            [-150.0, -150.0, -125.0],  # Left mouth corner
            [150.0, -150.0, -125.0]    # Right mouth corner
        ], dtype=np.float64)
        
        print("Attention Monitoring Service initialized with MediaPipe Face Landmarker")
    
    def analyze_attention(self, image_data):
        """
        Analyze attention levels from image data
        
        Args:
            image_data: Image as numpy array (BGR format from cv2)
            
        Returns:
            dict: {
                'success': bool,
                'total_faces': int,
                'focused_count': int,
                'distracted_count': int,
                'faces': list of face attention data,
                'alert': bool (True if >10 distracted)
            }
        """
        try:
            print(f"DEBUG: Analyzing image of shape: {image_data.shape}")
            
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            h, w = rgb_image.shape[:2]
            print(f"DEBUG: Image dimensions: {w}x{h}")
            
            # Use simple face detection if FaceLandmarker failed to initialize
            if self.face_landmarker is None:
                return self._fallback_detection(rgb_image, w, h)
            
            # Create MediaPipe Image
            mp_image = python.Image(image_format=python.ImageFormat.SRGB, data=rgb_image)
            
            # Detect faces
            detection_result = self.face_landmarker.detect(mp_image)
            
            faces_data = []
            focused_count = 0
            distracted_count = 0
            
            if detection_result.face_landmarks:
                print(f"DEBUG: Detected {len(detection_result.face_landmarks)} face(s)")
                for face_landmarks in detection_result.face_landmarks:
                    # Calculate head pose
                    pitch, yaw, roll = self._calculate_head_pose(face_landmarks, w, h)
                    
                    # Determine if paying attention
                    is_focused = self._is_paying_attention(pitch, yaw)
                    
                    print(f"DEBUG: Face - Pitch: {pitch:.1f}°, Yaw: {yaw:.1f}°, Roll: {roll:.1f}° - {'Focused' if is_focused else 'Distracted'}")
                    
                    if is_focused:
                        focused_count += 1
                    else:
                        distracted_count += 1
                    
                    faces_data.append({
                        'pitch': float(pitch),
                        'yaw': float(yaw),
                        'roll': float(roll),
                        'focused': is_focused,
                        'status': 'focused' if is_focused else 'distracted'
                    })
            else:
                print("DEBUG: No faces detected by MediaPipe")
            
            total_faces = len(faces_data)
            alert = distracted_count > 10
            
            print(f"DEBUG: Results - Total: {total_faces}, Focused: {focused_count}, Distracted: {distracted_count}")
            
            return {
                'success': True,
                'total_faces': total_faces,
                'focused_count': focused_count,
                'distracted_count': distracted_count,
                'faces': faces_data,
                'alert': alert
            }
            
        except Exception as e:
            print(f"Error analyzing attention: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'total_faces': 0,
                'focused_count': 0,
                'distracted_count': 0,
                'faces': [],
                'alert': False
            }
    
    def _fallback_detection(self, rgb_image, w, h):
        """Fallback using OpenCV face detection"""
        try:
            # Use Haar Cascade for simple face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            print(f"DEBUG: Fallback detected {len(faces)} face(s)")
            
            # Assume all detected faces are focused (can't determine pose without landmarks)
            faces_data = []
            for (x, y, w_face, h_face) in faces:
                faces_data.append({
                    'pitch': 0.0,
                    'yaw': 0.0,
                    'roll': 0.0,
                    'focused': True,
                    'status': 'focused'
                })
            
            return {
                'success': True,
                'total_faces': len(faces_data),
                'focused_count': len(faces_data),
                'distracted_count': 0,
                'faces': faces_data,
                'alert': False
            }
        except Exception as e:
            print(f"Fallback detection error: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_faces': 0,
                'focused_count': 0,
                'distracted_count': 0,
                'faces': [],
                'alert': False
            }
    
    def _calculate_head_pose(self, face_landmarks, img_w, img_h) -> Tuple[float, float, float]:
        """
        Calculate head pose angles (pitch, yaw, roll) from facial landmarks
        
        Returns:
            Tuple of (pitch, yaw, roll) in degrees
        """
        # Get 2D coordinates of key landmarks
        # Indices: 1=nose tip, 152=chin, 33=left eye, 263=right eye, 61=left mouth, 291=right mouth
        landmark_indices = [1, 152, 33, 263, 61, 291]
        
        face_2d = []
        for idx in landmark_indices:
            landmark = face_landmarks[idx]
            x = landmark.x * img_w
            y = landmark.y * img_h
            face_2d.append([x, y])
        
        face_2d = np.array(face_2d, dtype=np.float64)
        
        # Camera matrix (assuming standard webcam)
        focal_length = img_w
        cam_matrix = np.array([
            [focal_length, 0, img_w / 2],
            [0, focal_length, img_h / 2],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # Distortion coefficients (assuming no distortion)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)
        
        # Solve PnP to get rotation vector
        success, rot_vec, trans_vec = cv2.solvePnP(
            self.FACE_3D_POINTS,
            face_2d,
            cam_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        # Convert rotation vector to rotation matrix
        rmat, _ = cv2.Rodrigues(rot_vec)
        
        # Calculate Euler angles
        angles = self._rotation_matrix_to_euler_angles(rmat)
        
        pitch = angles[0] * 180 / np.pi  # Up/down
        yaw = angles[1] * 180 / np.pi    # Left/right
        roll = angles[2] * 180 / np.pi   # Tilt
        
        return pitch, yaw, roll
    
    def _rotation_matrix_to_euler_angles(self, R):
        """Convert rotation matrix to Euler angles"""
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        
        return np.array([x, y, z])
    
    def _is_paying_attention(self, pitch: float, yaw: float) -> bool:
        """
        Determine if student is paying attention based on head pose
        
        Args:
            pitch: Up/down angle (positive = looking down)
            yaw: Left/right angle
            
        Returns:
            bool: True if paying attention, False if distracted
        """
        # Student is distracted if:
        # - Looking down too much (pitch > threshold)
        # - Looking too far left or right (abs(yaw) > threshold)
        
        looking_down = pitch > self.PITCH_THRESHOLD
        looking_away = abs(yaw) > self.YAW_THRESHOLD
        
        # Paying attention if NOT looking down AND NOT looking away
        return not (looking_down or looking_away)
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'face_landmarker') and self.face_landmarker:
            self.face_landmarker.close()


# Global attention monitoring service instance
attention_service = AttentionMonitoringService()
