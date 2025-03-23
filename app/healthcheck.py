from flask import Blueprint

healthcheck_bp = Blueprint('healthcheck', __name__)

@healthcheck_bp.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return "OK", 200 