#!/usr/bin/env python3
"""
Script to sanitize environment files by removing sensitive information.
Use before committing changes to ensure no API keys or secrets are exposed.
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Patterns to detect sensitive information
SENSITIVE_PATTERNS = [
    # OpenAI API keys
    (r'OPENAI_API_KEY=sk-[A-Za-z0-9_\-]{30,}', 'OPENAI_API_KEY=your_openai_api_key_here'),
    # OpenRouter API keys
    (r'OPENROUTER_API_KEY=sk-or-[A-Za-z0-9_\-]{30,}', '#OPENROUTER_API_KEY=your_openrouter_api_key_here'),
    # General API keys
    (r'API_KEY=[A-Za-z0-9_\-]{20,}', 'API_KEY=your_api_key_here'),
    # Secret keys
    (r'SECRET_KEY=[A-Za-z0-9_\-]{20,}', 'SECRET_KEY=your_secret_key_here'),
]

def sanitize_file(file_path, dry_run=False):
    """Sanitize a single environment file."""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all sanitization patterns
        for pattern, replacement in SENSITIVE_PATTERNS:
            content = re.sub(pattern, replacement, content)
        
        # Check if anything was changed
        if content == original_content:
            logger.info(f"No sensitive information found in {file_path}")
            return True
        
        if dry_run:
            logger.warning(f"Sensitive information would be sanitized in {file_path} (dry run)")
            return False
        
        # Write sanitized content back to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Sanitized sensitive information in {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error sanitizing {file_path}: {str(e)}")
        return False

def sanitize_all_env_files(dry_run=False):
    """Sanitize all environment files in the project."""
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    
    # Define paths to check
    env_files = [
        root_dir / '.env',
        root_dir / '.env.example',
        root_dir / 'config' / 'docker' / '.env'
    ]
    
    success = True
    for env_file in env_files:
        if env_file.exists():
            if not sanitize_file(env_file, dry_run):
                success = False
    
    return success

if __name__ == "__main__":
    # Check for command line arguments
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        logger.info("Running in dry-run mode (no changes will be made)")
    
    logger.info("Sanitizing environment files...")
    if sanitize_all_env_files(dry_run):
        logger.info("Environment file sanitization completed")
        sys.exit(0)
    else:
        logger.error("Environment file sanitization encountered issues")
        sys.exit(1) 