"""
WSGI entry point for the Music Mix Analyzer application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app factory function
from app import create_app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Create error image directory if it doesn't exist
    os.makedirs('app/static/img', exist_ok=True)
    
    # In Docker, we need to listen on 0.0.0.0
    app.run(host='0.0.0.0', port=5001, debug=False) 