# This file makes the directory a Python package

"""
API package for the Music Mix Analyzer application
"""

import os
from functools import wraps
from flask import request, jsonify, current_app

def validate_api_key():
    """Validate the API key provided in the request."""
    # Get API key from header or query param
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    
    # Get the valid API key from environment variable
    valid_api_key = os.environ.get('API_KEY')
    
    # If no API key is configured, reject all requests
    if not valid_api_key:
        return False
    
    # Compare the provided key with the valid key
    return api_key == valid_api_key

def require_api_key(f):
    """Decorator to require API key for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_api_key():
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Valid API key is required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function
