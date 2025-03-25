#!/usr/bin/env python3
"""
Project consistency checker script.
Runs all consistency checks and reports any issues found.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f'consistency_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger(__name__)

def run_check(script_path, description):
    """Run a check script and report results"""
    logger.info(f"Running {description}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Log output regardless of success/failure
        for line in result.stdout.splitlines():
            if line.strip():
                logger.info(f"  {line}")
        
        if result.returncode != 0:
            logger.error(f"{description} failed with code {result.returncode}")
            for line in result.stderr.splitlines():
                if line.strip():
                    logger.error(f"  {line}")
            return False
        
        logger.info(f"{description} completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running {description}: {str(e)}")
        return False

def check_embedded_css_js():
    """Check for embedded CSS and JS in HTML files"""
    logger.info("Checking for embedded CSS and JS in HTML templates...")
    
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    templates_dir = root_dir / 'app' / 'templates'
    
    # Patterns to search for
    patterns = [
        '<style>', 
        '<script>', 
        '<script type="text/javascript">'
    ]
    
    # Exceptions for legitimate inline scripts
    exceptions = [
        '<script type="application/ld+json">',
        'var MATOMO_URL',
        'var MATOMO_SITE_ID'
    ]
    
    issues = []
    
    # Walk through all HTML files
    for html_file in templates_dir.glob('**/*.html'):
        with open(html_file, 'r') as f:
            content = f.read()
            
        # Check each pattern
        for pattern in patterns:
            if pattern in content:
                # Check if this is an exception
                is_exception = False
                for exc in exceptions:
                    if exc in content:
                        is_exception = True
                        break
                
                if not is_exception:
                    rel_path = html_file.relative_to(root_dir)
                    issues.append(f"Embedded {pattern} found in {rel_path}")
    
    # Report issues
    if issues:
        logger.warning("Embedded CSS/JS issues found:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"{i}. {issue}")
        return False
    
    logger.info("✓ No embedded CSS/JS issues found")
    return True

def check_uploads_directory():
    """Check if the uploads directory is correct and no uploads in static"""
    logger.info("Checking uploads directory configuration...")
    
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    
    # Locations to check
    root_uploads = root_dir / 'uploads'
    static_uploads = root_dir / 'app' / 'static' / 'uploads'
    
    issues = []
    
    # Check root uploads exists
    if not root_uploads.exists():
        issues.append("Root uploads directory doesn't exist")
    else:
        logger.info("✓ Root uploads directory exists")
    
    # Check if static uploads exists but should not have content
    if static_uploads.exists() and any(static_uploads.iterdir()):
        issues.append("app/static/uploads directory contains files that should be in root uploads/")
    
    # Report issues
    if issues:
        logger.warning("Uploads directory issues found:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"{i}. {issue}")
        return False
    
    logger.info("✓ Uploads directory configuration is correct")
    return True

def check_docker_configuration():
    """Check Docker configuration files consistency"""
    logger.info("Checking Docker configuration consistency...")
    
    script_dir = Path(__file__).parent.absolute()
    root_dir = script_dir.parent
    
    # Locations to check
    docker_config_dir = root_dir / 'config' / 'docker'
    root_dockerfile = root_dir / 'Dockerfile'
    root_compose = root_dir / 'docker-compose.yml'
    
    issues = []
    
    # Check Docker config directory exists
    if not docker_config_dir.exists():
        issues.append("Docker configuration directory (config/docker/) doesn't exist")
    else:
        logger.info("✓ Docker configuration directory exists")
    
    # Check Docker files in config directory
    if docker_config_dir.exists():
        docker_files = list(docker_config_dir.glob('Dockerfile'))
        if not docker_files:
            issues.append("Dockerfile not found in config/docker/")
    
    # Report issues
    if issues:
        logger.warning("Docker configuration issues found:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"{i}. {issue}")
        return False
    
    logger.info("✓ Docker configuration appears to be consistent")
    return True

def main():
    """Main function to run all consistency checks"""
    logger.info("Starting project consistency checks...")
    
    script_dir = Path(__file__).parent.absolute()
    
    checks = [
        (script_dir / 'check_env_consistency.py', "Environment file consistency check"),
        # Add other standalone check scripts here
    ]
    
    # Track overall success
    all_checks_passed = True
    
    # Run standalone check scripts
    for script_path, description in checks:
        if script_path.exists():
            if not run_check(script_path, description):
                all_checks_passed = False
        else:
            logger.warning(f"Check script not found: {script_path}")
    
    # Run integrated checks
    if not check_embedded_css_js():
        all_checks_passed = False
    
    if not check_uploads_directory():
        all_checks_passed = False
    
    if not check_docker_configuration():
        all_checks_passed = False
    
    # Report overall result
    if all_checks_passed:
        logger.info("✅ All consistency checks passed")
        return 0
    else:
        logger.warning("⚠️ Some consistency checks failed. See log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 