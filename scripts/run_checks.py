#!/usr/bin/env python3
"""
Comprehensive check runner for the Music Mix Analyzer project.
This script runs all check scripts to ensure the project is configured correctly.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Add the root directory to the path to ensure imports work
script_dir = Path(__file__).parent.absolute()
root_dir = script_dir.parent
sys.path.insert(0, str(root_dir))

def run_checks(args):
    """Run selected checks based on provided arguments"""
    script_dir = Path(__file__).parent.absolute()
    checks_dir = script_dir / 'checks'
    
    # Track success across all checks
    all_checks_passed = True
    
    # Run project consistency check (includes many sub-checks)
    if args.all or args.project:
        logger.info("Running project consistency check...")
        try:
            sys.path.insert(0, str(checks_dir))
            from check_project_consistency import main as check_project
            if not check_project():
                all_checks_passed = False
                logger.error("Project consistency check failed")
            else:
                logger.info("Project consistency check passed")
        except Exception as e:
            all_checks_passed = False
            logger.error(f"Error running project consistency check: {str(e)}")
    
    # Run security check
    if args.all or args.security:
        logger.info("Running security check...")
        try:
            from scripts.checks.security_check import main as security_check
            if not security_check():
                all_checks_passed = False
                logger.error("Security check failed")
            else:
                logger.info("Security check passed")
        except Exception as e:
            all_checks_passed = False
            logger.error(f"Error running security check: {str(e)}")
    
    # Run environment check
    if args.all or args.env:
        logger.info("Running environment check...")
        try:
            from scripts.checks.check_environment import main as check_env
            if not check_env():
                all_checks_passed = False
                logger.error("Environment check failed")
            else:
                logger.info("Environment check passed")
        except Exception as e:
            all_checks_passed = False
            logger.error(f"Error running environment check: {str(e)}")
    
    # Run imports check
    if args.all or args.imports:
        logger.info("Running imports check...")
        try:
            from scripts.checks.check_imports import main as check_imports
            if not check_imports():
                all_checks_passed = False
                logger.error("Imports check failed")
            else:
                logger.info("Imports check passed")
        except Exception as e:
            all_checks_passed = False
            logger.error(f"Error running imports check: {str(e)}")
    
    # Run uploads directory check
    if args.all or args.uploads:
        logger.info("Running uploads directory check...")
        try:
            from scripts.checks.check_uploads_dir import main as check_uploads
            if not check_uploads():
                all_checks_passed = False
                logger.error("Uploads directory check failed")
            else:
                logger.info("Uploads directory check passed")
        except Exception as e:
            all_checks_passed = False
            logger.error(f"Error running uploads directory check: {str(e)}")
    
    # Return overall success status
    return all_checks_passed

def main():
    """Main function to parse arguments and run checks"""
    parser = argparse.ArgumentParser(
        description="Run checks for the Music Mix Analyzer project"
    )
    
    # Add arguments for different types of checks
    parser.add_argument(
        '--all', '-a', action='store_true',
        help="Run all checks"
    )
    parser.add_argument(
        '--project', '-p', action='store_true',
        help="Run project consistency check"
    )
    parser.add_argument(
        '--security', '-s', action='store_true',
        help="Run security check"
    )
    parser.add_argument(
        '--env', '-e', action='store_true',
        help="Run environment check"
    )
    parser.add_argument(
        '--imports', '-i', action='store_true',
        help="Run imports check"
    )
    parser.add_argument(
        '--uploads', '-u', action='store_true',
        help="Run uploads directory check"
    )
    
    args = parser.parse_args()
    
    # If no specific check is selected, run all checks
    if not (args.all or args.project or args.security or args.env or 
            args.imports or args.uploads):
        args.all = True
    
    # Run the selected checks
    logger.info("Starting checks...")
    if run_checks(args):
        logger.info("All checks passed successfully!")
        return 0
    else:
        logger.error("One or more checks failed. Please fix the issues and run the checks again.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 