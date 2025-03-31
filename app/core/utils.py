"""
Utility functions for audio file handling and other common operations
"""

import os
import uuid
from werkzeug.utils import secure_filename

def get_file_extension(filename):
    """
    Extract the file extension from a filename
    
    Args:
        filename: The filename to extract the extension from
        
    Returns:
        The file extension without the dot
    """
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()

def is_valid_audio_file(filename):
    """
    Check if the file has a valid audio extension
    
    Args:
        filename: The filename to check
        
    Returns:
        Boolean indicating if the file has a valid audio extension
    """
    allowed_extensions = {'mp3', 'wav', 'flac', 'aiff', 'ogg'}
    return '.' in filename and get_file_extension(filename) in allowed_extensions

def generate_unique_filename(filename):
    """
    Generate a unique filename for an uploaded file
    
    Args:
        filename: The original filename
        
    Returns:
        A unique filename with the same extension
    """
    extension = get_file_extension(filename)
    unique_id = uuid.uuid4().hex
    
    if extension:
        return f"{unique_id}.{extension}"
    return unique_id 