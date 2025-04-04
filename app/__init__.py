"""
Music Mix Analyzer - A web application for analyzing audio mixes
"""

import os
from flask import Flask, current_app, request, jsonify, redirect
import json
import numpy as np
from dotenv import load_dotenv, find_dotenv
from flask.json.provider import DefaultJSONProvider
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

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
        MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100MB max upload
        VERSION=datetime.now().strftime("%Y%m%d%H%M%S"),  # Dynamic version based on timestamp
        LAST_UPDATED=datetime.now().strftime("%Y-%m-%d"),  # Current date for Schema.org dateModified
        FORCE_HTTPS=os.environ.get('FORCE_HTTPS', 'false').lower() == 'true',
        # URL configuration
        BASE_URL=os.environ.get('BASE_URL', ''),  # Base URL for the application (e.g., http://localhost:5001)
        CANONICAL_DOMAIN=os.environ.get('CANONICAL_DOMAIN', ''),  # Canonical domain for the application
        USE_RELATIVE_URLS=os.environ.get('USE_RELATIVE_URLS', 'true').lower() == 'true'  # Use relative URLs for forms and links
    )
    
    # Load configuration based on environment
    if os.environ.get('FLASK_ENV') == 'production':
        from config.config import ProductionConfig
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)
        # Docker environments might not have HTTPS, so respect the environment variable
        force_https = os.environ.get('FORCE_HTTPS', 'true').lower()
        app.config['FORCE_HTTPS'] = force_https == 'true'
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
    
    # Initialize database
    with app.app_context():
        from app.core.database import initialize_database
        if initialize_database():
            app.logger.info("Database initialized successfully")
        else:
            app.logger.warning("Failed to initialize database")
    
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
    
    # Add HTTP to HTTPS redirect middleware
    @app.before_request
    def redirect_to_https():
        """Redirect all HTTP requests to HTTPS"""
        # Skip HTTPS redirection for development or if explicitly disabled
        if app.debug or os.environ.get('FORCE_HTTPS', 'false').lower() == 'false':
            return None
            
        # Skip for Docker environments unless they have proper HTTPS setup
        if os.environ.get('RUN_ENV') == 'docker' and not os.environ.get('DOCKER_HAS_HTTPS'):
            return None
            
        # Check for proxy headers first (common when behind load balancers)
        proto = request.headers.get('X-Forwarded-Proto')
        host = request.headers.get('X-Forwarded-Host') or request.host
        
        # Special handling for sitemap.xml to prevent multiple redirects
        if request.path == '/sitemap.xml':
            if proto == 'http' or (proto is None and request.scheme == 'http'):
                # Explicitly redirect sitemap.xml to HTTPS
                return redirect(f"https://{host}/sitemap.xml", code=301)
        
        # Only redirect if:
        # 1. FORCE_HTTPS is enabled
        # 2. The request came via HTTP protocol or X-Forwarded-Proto is 'http'
        if app.config['FORCE_HTTPS'] and (proto == 'http' or (proto is None and request.scheme == 'http')):
            # Construct URL with https
            url = f"https://{host}{request.path}"
            if request.query_string:
                url += f"?{request.query_string.decode('utf-8')}"
            # Return a 301 permanent redirect
            return redirect(url, code=301)
    
    # Configure security headers
    @app.after_request
    def add_security_headers(response):
        # Content Security Policy
        csp = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://seo.optagonen.se https://*.cloudflareinsights.com https://cdn.plot.ly",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://unpkg.com",
            "img-src 'self' data: https://seo.optagonen.se https://img.buymeacoffee.com",
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com",
            "connect-src 'self' https://seo.optagonen.se https://*.cloudflareinsights.com",
            "media-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "base-uri 'self'"
        ]
        
        response.headers['Content-Security-Policy'] = "; ".join(csp)
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add cache control headers for CSS and JavaScript files
        if response.mimetype == 'text/css' or request.path.endswith('.css'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif response.mimetype == 'application/javascript' or request.path.endswith('.js'):
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
    
    # Add template context processor to force HTTPS URLs
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context"""
        
        def secure_url(url):
            """Make URL secure (https) if FORCE_HTTPS is enabled"""
            if not url or url.startswith(('mailto:', '#', 'tel:', '//')):
                return url
                
            # If we use relative URLs, always return relative URLs
            if app.config.get('USE_RELATIVE_URLS', True) and url.startswith('/'):
                return url
                
            # If it's already HTTPS, or it's not a URL, return as is
            if not url.startswith('http:'):
                return url
                
            # If FORCE_HTTPS is enabled, convert http:// to https://
            if app.config['FORCE_HTTPS'] and url and url.startswith('http:'):
                return url.replace('http:', 'https:', 1)
            
            # If BASE_URL is configured, use it for absolute URLs
            base_url = app.config.get('BASE_URL')
            if base_url and url.startswith('/'):
                # Remove trailing slash from base_url if present
                if base_url.endswith('/'):
                    base_url = base_url[:-1]
                return f"{base_url}{url}"
                
            return url
            
        # Return the function to make it available in templates
        return dict(secure_url=secure_url)
        
    @app.context_processor
    def asset_processor():
        """Add asset versioning to template context"""
        
        def versioned_asset(filename):
            """Add version to asset filename for cache busting"""
            version = app.config.get('VERSION', datetime.now().strftime("%Y%m%d%H%M%S"))
            
            # Add query string with version
            if '?' in filename:
                return f"{filename}&v={version}"
            else:
                return f"{filename}?v={version}"
                
        # Include base_url function to generate proper URLs for assets
        def base_url(path=None):
            """Generate a URL with the correct base and protocol"""
            # Get configured base URL or construct from request
            configured_base = app.config.get('BASE_URL')
            if configured_base:
                # Remove trailing slash
                if configured_base.endswith('/'):
                    configured_base = configured_base[:-1]
                    
                # Add path if provided
                if path:
                    # Ensure path starts with a slash
                    if not path.startswith('/'):
                        path = f"/{path}"
                    return f"{configured_base}{path}"
                return configured_base
                
            # Construct from current request
            protocol = 'https' if app.config.get('FORCE_HTTPS') else request.scheme
            host = app.config.get('CANONICAL_DOMAIN') or request.host
            
            if path:
                # Ensure path starts with a slash
                if not path.startswith('/'):
                    path = f"/{path}"
                return f"{protocol}://{host}{path}"
            
            return f"{protocol}://{host}"
            
        return dict(versioned_asset=versioned_asset, base_url=base_url)
        
    # Add template global for building properly formatted URLs
    @app.template_global()
    def url_for_with_base(endpoint, **values):
        """Override url_for to include BASE_URL when needed"""
        from flask import url_for
        
        # Get the URL using Flask's url_for
        url = url_for(endpoint, **values)
        
        # If using relative URLs and the URL is relative, return as is
        if app.config.get('USE_RELATIVE_URLS', True) and url.startswith('/'):
            return url
            
        # Get the base URL from configuration
        base_url = app.config.get('BASE_URL')
        if base_url and not url.startswith(('http://', 'https://')):
            # Remove trailing slash from base_url if present
            if base_url.endswith('/'):
                base_url = base_url[:-1]
                
            # Make sure URL starts with a slash
            if not url.startswith('/'):
                url = f"/{url}"
                
            return f"{base_url}{url}"
            
        return url
    
    return app 