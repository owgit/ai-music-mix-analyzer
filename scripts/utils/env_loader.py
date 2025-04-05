#!/usr/bin/env python3
"""
Environment variable loader for the Music Mix Analyzer project.
This module provides a consistent way to load environment variables
following the project's configuration hierarchy.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_environment():
    """
    Load environment variables following the hierarchy:
    1. Variables already in the environment
    2. Root .env file
    3. Docker environment file (if running in Docker)
    4. Default values
    
    Returns:
        bool: True if environment was loaded, False if it was already loaded
    """
    # Check if environment is already loaded
    if os.environ.get('ENV_LOADED') == 'true':
        logger.debug("Environment already loaded, skipping")
        return False
    
    # Get the project root directory
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    
    # Define paths to environment files
    root_env = root_dir / '.env'
    docker_env = root_dir / 'config' / 'docker' / '.env'
    
    # Load root .env file first (if it exists)
    if root_env.exists():
        logger.debug(f"Loading environment from {root_env}")
        load_dotenv(dotenv_path=root_env)
    else:
        logger.warning(f"Root .env file not found at {root_env}")
        logger.warning("Copy .env.example to .env and set your environment variables")
    
    # Load Docker environment if running in Docker and file exists
    if os.environ.get('DOCKER_ENV') == 'true' and docker_env.exists():
        logger.debug(f"Loading Docker environment from {docker_env}")
        # Docker env overrides root env variables
        load_dotenv(dotenv_path=docker_env, override=True)
    
    # Check for required environment variables
    check_required_variables()
    
    # Mark environment as loaded
    os.environ['ENV_LOADED'] = 'true'
    return True

def check_required_variables():
    """Check for required environment variables and set defaults if missing"""
    # API provider selection
    if not os.environ.get('AI_PROVIDER'):
        logger.warning("AI_PROVIDER not set, defaulting to 'openai'")
        os.environ['AI_PROVIDER'] = 'openai'
    
    # Check for API keys based on provider
    ai_provider = os.environ.get('AI_PROVIDER')
    if ai_provider == 'openai' and not os.environ.get('OPENAI_API_KEY'):
        logger.warning("OPENAI_API_KEY not set, AI features will not work")
    elif ai_provider == 'openrouter' and not os.environ.get('OPENROUTER_API_KEY'):
        logger.warning("OPENROUTER_API_KEY not set, AI features will not work")
    
    # Check for API model based on provider
    if ai_provider == 'openai' and not os.environ.get('OPENAI_MODEL'):
        logger.warning("OPENAI_MODEL not set, defaulting to 'gpt-4o-mini'")
        os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'
    elif ai_provider == 'openrouter' and not os.environ.get('OPENROUTER_MODEL'):
        logger.warning("OPENROUTER_MODEL not set, please set in .env")
    
    # Check for OpenRouter timeout threshold
    if ai_provider == 'openrouter' and not os.environ.get('OPENROUTER_TIMEOUT_THRESHOLD'):
        logger.info("OPENROUTER_TIMEOUT_THRESHOLD not set, defaulting to 30 seconds")
        os.environ['OPENROUTER_TIMEOUT_THRESHOLD'] = '30'
    
    # Check for security-related variables
    if not os.environ.get('SECRET_KEY'):
        logger.warning("SECRET_KEY not set, please generate one with scripts/generate_secret_key.py")
    
    if not os.environ.get('API_KEY'):
        logger.warning("API_KEY not set, API endpoints will reject all requests")
    
    # Set Flask environment if not set
    if not os.environ.get('FLASK_ENV'):
        logger.info("FLASK_ENV not set, defaulting to 'development'")
        os.environ['FLASK_ENV'] = 'development'
    
    # Set Flask app if not set
    if not os.environ.get('FLASK_APP'):
        logger.info("FLASK_APP not set, defaulting to 'app.py'")
        os.environ['FLASK_APP'] = 'app.py'

if __name__ == "__main__":
    # When run directly, load environment and print status
    if load_environment():
        logger.info("Environment loaded successfully")
    else:
        logger.info("Environment was already loaded")
    
    # Print current settings (for debugging)
    logger.info(f"AI Provider: {os.environ.get('AI_PROVIDER')}")
    logger.info(f"OpenAI Model: {os.environ.get('OPENAI_MODEL')}")
    logger.info(f"OpenRouter Model: {os.environ.get('OPENROUTER_MODEL')}")
    logger.info(f"Flask Environment: {os.environ.get('FLASK_ENV')}")
    logger.info(f"Analytics Enabled: {os.environ.get('ENABLE_ANALYTICS')}") 