#!/usr/bin/env python3
"""
Script to migrate uploads from app/static/uploads to the root uploads directory.
This helps maintain consistency according to the project rules.
"""

import os
import shutil
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', f'upload_migration_{datetime.now().strftime("%Y%m%d")}.log'))
    ]
)

logger = logging.getLogger(__name__)

def migrate_uploads():
    """
    Migrate uploads from app/static/uploads to the root uploads directory
    """
    # Define directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    static_uploads_dir = os.path.join(root_dir, 'app', 'static', 'uploads')
    root_uploads_dir = os.path.join(root_dir, 'uploads')
    
    logger.info(f"Looking for files in {static_uploads_dir}")
    
    # Ensure root uploads directory exists
    os.makedirs(root_uploads_dir, exist_ok=True)
    
    # Check if static uploads directory exists
    if not os.path.exists(static_uploads_dir):
        logger.info("No static uploads directory found. Nothing to migrate.")
        return
    
    # Count files
    file_count = 0
    dir_count = 0
    
    # Walk through static uploads directory
    for root, dirs, files in os.walk(static_uploads_dir):
        # Get relative path
        rel_path = os.path.relpath(root, static_uploads_dir)
        target_dir = os.path.join(root_uploads_dir, rel_path) if rel_path != '.' else root_uploads_dir
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        dir_count += 1
        
        # Copy files
        for file in files:
            if file.startswith('.'):  # Skip hidden files
                continue
                
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            # Skip if target file already exists and is identical
            if os.path.exists(target_file) and os.path.getsize(source_file) == os.path.getsize(target_file):
                logger.debug(f"Skipping identical file: {file}")
                continue
                
            try:
                shutil.copy2(source_file, target_file)
                logger.info(f"Copied: {source_file} -> {target_file}")
                file_count += 1
            except Exception as e:
                logger.error(f"Error copying {source_file}: {e}")
    
    logger.info(f"Migration complete. {file_count} files and {dir_count} directories processed.")
    
    # No removal of the original files - we keep them as a backup
    logger.info("Files have been copied but not deleted from the original location.")
    logger.info("To remove original files, run with --remove argument")
    
    if '--remove' in sys.argv:
        logger.info("Removing original files...")
        try:
            shutil.rmtree(static_uploads_dir)
            os.makedirs(static_uploads_dir, exist_ok=True)  # Recreate empty directory
            logger.info("Original files removed successfully.")
        except Exception as e:
            logger.error(f"Error removing original files: {e}")

if __name__ == "__main__":
    logger.info("Starting upload migration script")
    migrate_uploads()
    logger.info("Upload migration script completed") 