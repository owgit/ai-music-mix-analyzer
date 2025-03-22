"""
WSGI entry point for the Music Mix Analyzer application
"""

import os
import sys
from dotenv import load_dotenv

# Try to load environment variables from multiple locations
if os.path.exists('.env'):
    load_dotenv()
elif os.path.exists('config/.env'):
    load_dotenv('config/.env')
else:
    print("Warning: No .env file found in root or config directory.")

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