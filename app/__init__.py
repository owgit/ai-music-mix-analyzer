"""
Music Mix Analyzer - A web application for analyzing audio mixes
"""

import os
from flask import Flask, current_app, request, jsonify
import json
import numpy as np
from dotenv import load_dotenv, find_dotenv
from flask.json.provider import DefaultJSONProvider
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import datetime

# Load environment variables from .env file only if not already loaded
if not os.environ.get('ENV_LOADED'):
    if os.path.exists('.env'):
        load_dotenv()
    elif os.path.exists('config/.env'):
        load_dotenv('config/.env')
    # Mark environment as loaded
    os.environ['ENV_LOADED'] = 'true'

# Custom JSON provider for Flask 2.3.x that handles NumPy types
class NumpyJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles NumPy types"""
    
    def dumps(self, obj, **kwargs):
        return super().dumps(obj, default=NumpyJSONEncoder.default, **kwargs)
    
    def loads(self, s, **kwargs):
        return super().loads(s, **kwargs)

# Custom JSON encoder for NumPy types
class NumpyJSONEncoder:
    """JSON encoder for numpy types"""
    @staticmethod
    def default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return None

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max upload
        VERSION=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),  # Dynamic version based on timestamp
        LAST_UPDATED=datetime.datetime.now().strftime("%Y-%m-%d"),  # Current date for Schema.org dateModified
    )
    
    # Load configuration based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        from config.config import ProductionConfig
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)
    else:
        from config.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)
    
    # Override with test config if passed
    if test_config is not None:
        app.config.from_mapping(test_config)
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure Flask to use our custom JSON provider (Flask 2.3.x compatible)
    app.json_provider_class = NumpyJSONProvider
    app.json = app.json_provider_class(app)
    
    # Configure rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    
    # Add a rate limit exceeded error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(error="Rate limit exceeded", message=str(e.description), 
                      retry_after=e.retry_after), 429
    
    # Check if API key is configured
    if not os.environ.get('API_KEY'):
        app.logger.warning(
            "API_KEY environment variable not set. "
            "API endpoints will reject all requests until a valid API key is configured."
        )
    
    # Configure security headers
    @app.after_request
    def add_security_headers(response):
        # Content Security Policy
        csp = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://seo.optagonen.se https://*.cloudflareinsights.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
            "img-src 'self' data: https://seo.optagonen.se",
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com",
            "connect-src 'self' https://seo.optagonen.se https://*.cloudflareinsights.com",
            "media-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'"
        ]
        
        response.headers['Content-Security-Policy'] = "; ".join(csp)
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add cache control headers for CSS files
        if response.mimetype == 'text/css' or request.path.endswith('.css'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        # Only set HSTS in production
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register health check
    from app.healthcheck import healthcheck_bp
    app.register_blueprint(healthcheck_bp)
    
    return app 