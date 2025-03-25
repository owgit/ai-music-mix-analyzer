#!/usr/bin/env python3
"""
Script to check the consistency of environment files.
Ensures that environment variables are properly organized according to project rules.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_env_consistency():
    """
    Check the consistency of environment files:
    - .env should exist in the root directory
    - Docker-specific environment should be in config/docker/.env
    - No redundant .env files in config/ directory
    """
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    
    # Define paths to check
    root_env = root_dir / '.env'
    config_env = root_dir / 'config' / '.env'
    docker_env = root_dir / 'config' / 'docker' / '.env'
    
    issues = []
    
    # Check for the root .env file
    if not root_env.exists():
        issues.append("Root .env file doesn't exist. Create one from .env.example")
    else:
        logger.info("✓ Root .env file exists")
    
    # Check for redundant config/.env file
    if config_env.exists():
        issues.append("Redundant .env file found in config/ directory. Use the root .env file instead.")
    else:
        logger.info("✓ No redundant .env file in config/ directory")
    
    # Check for Docker env file
    if docker_env.exists():
        logger.info("✓ Docker-specific .env file exists in config/docker/")
    else:
        issues.append("Docker-specific .env file doesn't exist in config/docker/. Consider creating one for Docker configuration.")
    
    # Report issues
    if issues:
        logger.warning("Environment file issues found:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"{i}. {issue}")
        return False
    
    logger.info("✓ Environment file setup is consistent with project rules")
    return True

if __name__ == "__main__":
    logger.info("Checking environment file consistency...")
    if not check_env_consistency():
        sys.exit(1)
    logger.info("Environment file check completed successfully") 