#!/usr/bin/env python3
"""
Music Mix Analyzer Management Script
Provides a unified interface for common project tasks:
- Running the application
- Running checks
- Setting up the environment
- Managing Docker containers
"""

import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Add the root directory to the path to ensure imports work properly
root_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(root_dir))

def run_app(args):
    """Run the Flask application"""
    try:
        # Import environment loader
        from scripts.utils.env_loader import load_environment
        load_environment()
    except ImportError:
        logger.warning("Could not import environment loader, using default loader")
        from dotenv import load_dotenv
        load_dotenv()
    
    debug_mode = not args.production
    port = args.port
    
    # Import and run the app
    try:
        import wsgi
        logger.info(f"Starting application on port {port} (debug: {debug_mode})")
        wsgi.app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        return False
    
    return True

def run_checks(args):
    """Run project checks"""
    check_args = []
    
    if args.all:
        check_args.append('--all')
    if args.project:
        check_args.append('--project')
    if args.security:
        check_args.append('--security')
    if args.env:
        check_args.append('--env')
    if args.imports:
        check_args.append('--imports')
    if args.uploads:
        check_args.append('--uploads')
    
    # If no specific check is selected, run all checks
    if not check_args:
        check_args.append('--all')
    
    try:
        script_path = Path(__file__).parent / 'scripts' / 'run_checks.py'
        cmd = [sys.executable, str(script_path)] + check_args
        logger.info(f"Running checks: {' '.join(check_args)}")
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Checks failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"Error running checks: {str(e)}")
        return False

def setup_environment(args):
    """Set up the project environment"""
    try:
        # Make sure the .env file exists
        if not os.path.exists('.env'):
            logger.info("Creating .env from .env.example")
            subprocess.run(['cp', '.env.example', '.env'], check=True)
        
        # Generate a secret key if requested
        if args.generate_key:
            logger.info("Generating secret key")
            try:
                from scripts.setup.generate_secret_key import generate_secret_key, update_env_file
                key = generate_secret_key()
                update_env_file(key)
            except ImportError:
                logger.warning("Could not import generate_secret_key module")
                # Run as a subprocess instead
                subprocess.run([sys.executable, 'scripts/setup/generate_secret_key.py', '--update-env'], check=True)
        
        # Run Apple Silicon setup if requested
        if args.apple_silicon:
            logger.info("Running Apple Silicon setup")
            setup_script = Path(__file__).parent / 'scripts' / 'setup' / 'setup_apple_silicon.sh'
            subprocess.run(['bash', str(setup_script)], check=True)
        
        return True
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        return False

def docker_command(args):
    """Run Docker-related commands"""
    try:
        if args.start:
            logger.info("Starting Docker containers")
            subprocess.run(['bash', 'scripts/docker/run.sh'], check=True)
        elif args.stop:
            logger.info("Stopping Docker containers")
            subprocess.run(['bash', 'scripts/docker/stop.sh'], check=True)
        elif args.update:
            logger.info("Updating Docker containers")
            subprocess.run(['bash', 'scripts/docker/update.sh'], check=True)
        else:
            logger.error("No Docker command specified")
            return False
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker command failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"Error running Docker command: {str(e)}")
        return False

def handle_security(args):
    """Handle security-related commands"""
    try:
        if args.sanitize:
            logger.info("Sanitizing environment files")
            try:
                from scripts.utils.sanitize_env import sanitize_all_env_files
                sanitize_all_env_files(args.dry_run)
            except ImportError:
                logger.warning("Could not import sanitize_env module")
                # Run as a subprocess instead
                cmd = [sys.executable, 'scripts/utils/sanitize_env.py']
                if args.dry_run:
                    cmd.append('--dry-run')
                subprocess.run(cmd, check=True)
        elif args.check:
            logger.info("Running security check")
            subprocess.run([sys.executable, 'scripts/checks/security_check.py'], check=True)
        else:
            logger.error("No security command specified")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error handling security command: {str(e)}")
        return False

def handle_maintenance(args):
    """Handle maintenance-related commands"""
    try:
        if args.cleanup_uploads:
            logger.info(f"Running uploads cleanup (retention: {args.days} days)")
            
            # Build command arguments
            cmd = [sys.executable, 'scripts/utils/cleanup_uploads.py']
            if args.dry_run:
                cmd.append('--dry-run')
            cmd.append(f'--days={args.days}')
            
            # Run the cleanup script
            subprocess.run(cmd, check=True)
            return True
        else:
            logger.error("No maintenance command specified")
            return False
    except Exception as e:
        logger.error(f"Error handling maintenance command: {str(e)}")
        return False

def run_tests(args):
    """Run tests with pytest"""
    try:
        # Check if pytest is installed
        import pytest
    except ImportError:
        logger.error("Pytest is not installed. Please install it with: pip install pytest")
        return False
    
    # Build pytest command arguments
    cmd = ['-v']  # Verbose output by default
    
    # Add test type based on arguments
    if args.unit:
        cmd.append('tests/unit/')
    elif args.integration:
        cmd.append('tests/integration/')
    elif args.e2e:
        cmd.append('tests/e2e/')
    elif args.path:
        cmd.append(args.path)
    else:
        # Run all tests by default
        cmd.append('tests/')
    
    # Add coverage reporting if requested
    if args.coverage:
        cmd.extend(['--cov=app', '--cov-report=term-missing'])
    
    # Run pytest with the constructed command
    logger.info(f"Running tests with pytest: {' '.join(cmd)}")
    result = pytest.main(cmd)
    return result == 0

def main():
    """Main function to parse arguments and run commands"""
    parser = argparse.ArgumentParser(
        description="Music Mix Analyzer Management Script"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Run application command
    run_parser = subparsers.add_parser('run', help='Run the Flask application')
    run_parser.add_argument('--production', action='store_true',
                           help='Run in production mode (no debug)')
    run_parser.add_argument('--port', type=int, default=5002,
                           help='Port to run the application on')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Run project checks')
    check_parser.add_argument('--all', '-a', action='store_true',
                             help='Run all checks')
    check_parser.add_argument('--project', '-p', action='store_true',
                             help='Run project consistency check')
    check_parser.add_argument('--security', '-s', action='store_true',
                             help='Run security check')
    check_parser.add_argument('--env', '-e', action='store_true',
                             help='Run environment check')
    check_parser.add_argument('--imports', '-i', action='store_true',
                             help='Run imports check')
    check_parser.add_argument('--uploads', '-u', action='store_true',
                             help='Run uploads directory check')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up the project environment')
    setup_parser.add_argument('--generate-key', '-g', action='store_true',
                             help='Generate a new secret key')
    setup_parser.add_argument('--apple-silicon', '-a', action='store_true',
                             help='Set up for Apple Silicon')
    
    # Docker command
    docker_parser = subparsers.add_parser('docker', help='Run Docker commands')
    docker_group = docker_parser.add_mutually_exclusive_group(required=True)
    docker_group.add_argument('--start', action='store_true',
                             help='Start Docker containers')
    docker_group.add_argument('--stop', action='store_true',
                             help='Stop Docker containers')
    docker_group.add_argument('--update', action='store_true',
                             help='Update Docker containers')
    
    # Security command
    security_parser = subparsers.add_parser('security', help='Security-related commands')
    security_group = security_parser.add_mutually_exclusive_group(required=True)
    security_group.add_argument('--sanitize', action='store_true',
                              help='Sanitize environment files')
    security_group.add_argument('--check', action='store_true',
                              help='Run security check')
    security_parser.add_argument('--dry-run', action='store_true',
                               help='Dry run (do not modify files)')
    
    # Maintenance command
    maintenance_parser = subparsers.add_parser('maintenance', help='Maintenance-related commands')
    maintenance_group = maintenance_parser.add_mutually_exclusive_group(required=True)
    maintenance_group.add_argument('--cleanup-uploads', action='store_true',
                                 help='Clean up old uploaded files')
    maintenance_parser.add_argument('--days', type=int, default=30,
                                  help='Number of days to retain files (default: 30)')
    maintenance_parser.add_argument('--dry-run', action='store_true',
                                  help='Dry run (do not delete files)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_group = test_parser.add_mutually_exclusive_group()
    test_group.add_argument('--unit', '-u', action='store_true',
                          help='Run unit tests')
    test_group.add_argument('--integration', '-i', action='store_true',
                          help='Run integration tests')
    test_group.add_argument('--e2e', '-e', action='store_true',
                          help='Run end-to-end tests')
    test_group.add_argument('--path', '-p', type=str,
                          help='Run tests at the specified path')
    test_parser.add_argument('--coverage', '-c', action='store_true',
                           help='Generate test coverage report')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == 'run':
        success = run_app(args)
    elif args.command == 'check':
        success = run_checks(args)
    elif args.command == 'setup':
        success = setup_environment(args)
    elif args.command == 'docker':
        success = docker_command(args)
    elif args.command == 'security':
        success = handle_security(args)
    elif args.command == 'maintenance':
        success = handle_maintenance(args)
    elif args.command == 'test':
        success = run_tests(args)
    else:
        parser.print_help()
        return 0
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 