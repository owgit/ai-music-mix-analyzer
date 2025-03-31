"""
Pytest configuration file for Music Mix Analyzer
"""

import sys
import os
import pytest
from pathlib import Path

# Add the project root to the path
root_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_dir))

# Import the app factory function for test fixtures
from app import create_app


@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    test_config = {
        'TESTING': True,
        'SERVER_NAME': 'localhost',
        'UPLOAD_FOLDER': '/tmp/uploads_test',
        'WTF_CSRF_ENABLED': False
    }
    
    # Create the test uploads folder
    os.makedirs(test_config['UPLOAD_FOLDER'], exist_ok=True)
    
    app = create_app(test_config)
    
    # Create a test context
    with app.app_context():
        yield app
    
    # Cleanup test files after the test
    import shutil
    if os.path.exists(test_config['UPLOAD_FOLDER']):
        shutil.rmtree(test_config['UPLOAD_FOLDER'])


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner() 