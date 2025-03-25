#!/usr/bin/env python3
"""
Script to clean up uploaded files that are older than 30 days.
This is part of the file retention policy to automatically delete old uploads.
"""

import os
import sys
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', f'uploads_cleanup_{datetime.now().strftime("%Y%m%d")}.log'))
    ]
)

logger = logging.getLogger(__name__)

def get_upload_dir():
    """Get the uploads directory path."""
    # Try to import app config to get UPLOAD_FOLDER
    try:
        script_dir = Path(__file__).parent.absolute()
        root_dir = script_dir.parent.parent  # Navigate to project root
        
        # Add project root to path for imports
        sys.path.insert(0, str(root_dir))
        
        # Import the app factory function
        from app import create_app
        app = create_app()
        with app.app_context():
            upload_folder = app.config['UPLOAD_FOLDER']
            return Path(upload_folder)
    except Exception as e:
        logger.warning(f"Could not get upload folder from app config: {str(e)}")
        
        # Fallback to default (project_root/uploads)
        script_dir = Path(__file__).parent.absolute()
        root_dir = script_dir.parent.parent  # Navigate to project root
        return root_dir / 'uploads'

def is_older_than_days(path, days):
    """Check if a file or directory is older than specified days."""
    # Get the modification time
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    cutoff_date = datetime.now() - timedelta(days=days)
    
    return mtime < cutoff_date

def cleanup_old_files(days=30, dry_run=False):
    """
    Clean up files that are older than the specified days.
    
    Args:
        days (int): Number of days to keep files (default: 30)
        dry_run (bool): If True, only log actions without deleting files
    
    Returns:
        tuple: (files_deleted, dirs_deleted, errors)
    """
    uploads_dir = get_upload_dir()
    logger.info(f"Checking for files older than {days} days in {uploads_dir}")
    
    if not os.path.exists(uploads_dir):
        logger.warning(f"Uploads directory does not exist: {uploads_dir}")
        return 0, 0, 0
    
    files_deleted = 0
    dirs_deleted = 0
    errors = 0
    
    # Process each subdirectory (each upload is in its own directory)
    for item in os.listdir(uploads_dir):
        item_path = os.path.join(uploads_dir, item)
        
        # Skip if not a directory
        if not os.path.isdir(item_path):
            continue
        
        try:
            if is_older_than_days(item_path, days):
                if dry_run:
                    logger.info(f"Would delete directory (older than {days} days): {item_path}")
                else:
                    logger.info(f"Deleting directory (older than {days} days): {item_path}")
                    shutil.rmtree(item_path)
                    dirs_deleted += 1
                    files_deleted += 1  # At least one file per directory
        except Exception as e:
            logger.error(f"Error processing {item_path}: {str(e)}")
            errors += 1
    
    if dry_run:
        logger.info(f"Dry run completed. Would delete {dirs_deleted} directories containing uploads older than {days} days.")
    else:
        logger.info(f"Cleanup completed. Deleted {dirs_deleted} directories containing uploads older than {days} days.")
    
    return files_deleted, dirs_deleted, errors

if __name__ == "__main__":
    # Parse command line arguments
    dry_run = "--dry-run" in sys.argv
    
    # Get retention days (default: 30)
    retention_days = 30
    for arg in sys.argv:
        if arg.startswith("--days="):
            try:
                retention_days = int(arg.split("=")[1])
            except (ValueError, IndexError):
                logger.error(f"Invalid days value: {arg}")
                sys.exit(1)
    
    logger.info(f"Running uploads cleanup with {retention_days} days retention" + 
               " (dry run)" if dry_run else "")
    
    files, dirs, errors = cleanup_old_files(retention_days, dry_run)
    
    if errors > 0:
        logger.warning(f"{errors} errors occurred during cleanup")
        sys.exit(1)
    
    logger.info("Uploads cleanup completed successfully")
    sys.exit(0) 