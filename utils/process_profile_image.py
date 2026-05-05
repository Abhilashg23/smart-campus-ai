"""
Utility functions for processing profile images and extracting face encodings
"""
import face_recognition
import numpy as np
from PIL import Image
import io


def extract_face_encoding(image_file):
    """
    Extract face encoding from an uploaded image file
    
    Args:
        image_file: FileStorage object from Flask request.files
        
    Returns:
        tuple: (success: bool, encoding: np.array or None, error_message: str or None)
    """
    try:
        # Read image file
        image_bytes = image_file.read()
        image_file.seek(0)  # Reset file pointer for potential re-use
        
        # Load image using face_recognition
        image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(image)
        
        # Validate: Must have exactly one face
        if len(face_locations) == 0:
            return False, None, "No face detected in the image. Please upload a clear photo with a visible face."
        
        if len(face_locations) > 1:
            return False, None, f"Multiple faces detected ({len(face_locations)} faces). Please upload an image with only one person."
        
        # Extract face encoding
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            return False, None, "Could not extract face features. Please upload a clearer image."
        
        encoding = face_encodings[0]
        
        return True, encoding, None
        
    except Exception as e:
        return False, None, f"Error processing image: {str(e)}"


def validate_image_file(file):
    """
    Validate that uploaded file is a valid image
    
    Args:
        file: FileStorage object from Flask request.files
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename:
        return False, "File must have an extension"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size (max 5MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        return False, "File size too large. Maximum size is 5MB"
    
    # Try to open as image
    try:
        image_bytes = file.read()
        file.seek(0)  # Reset file pointer
        Image.open(io.BytesIO(image_bytes))
        return True, None
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def encoding_to_bytes(encoding):
    """
    Convert numpy face encoding array to bytes for database storage
    
    Args:
        encoding: numpy array from face_recognition
        
    Returns:
        bytes: Serialized encoding
    """
    import pickle
    return pickle.dumps(encoding)


def bytes_to_encoding(encoding_bytes):
    """
    Convert bytes back to numpy face encoding array
    
    Args:
        encoding_bytes: bytes from database
        
    Returns:
        numpy array: Face encoding
    """
    import pickle
    return pickle.loads(encoding_bytes)
