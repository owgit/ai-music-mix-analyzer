#!/usr/bin/env python3
"""
Check if the uploads directory exists and is writable.
This script helps diagnose file upload issues.
"""

import os
import sys
import tempfile

def check_directory(directory_path):
    """Check if a directory exists and is writable."""
    print(f"Checking directory: {directory_path}")
    
    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"ERROR: Directory does not exist: {directory_path}")
        try:
            print(f"Attempting to create directory...")
            os.makedirs(directory_path, exist_ok=True)
            print(f"Successfully created directory: {directory_path}")
        except Exception as e:
            print(f"Failed to create directory: {str(e)}")
            return False
    
    # Check if it's a directory
    if not os.path.isdir(directory_path):
        print(f"ERROR: Path exists but is not a directory: {directory_path}")
        return False
    
    # Check if directory is writable
    try:
        temp_file = os.path.join(directory_path, f"test_write_{os.getpid()}.tmp")
        with open(temp_file, 'w') as f:
            f.write("Test write")
        os.remove(temp_file)
        print(f"SUCCESS: Directory is writable: {directory_path}")
        return True
    except Exception as e:
        print(f"ERROR: Directory is not writable: {str(e)}")
        return False

def main():
    """Check the uploads directories used by the application."""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check the main uploads directory
    main_uploads = os.path.join(script_dir, 'uploads')
    check_directory(main_uploads)
    
    # Check the app/static/uploads directory
    app_uploads = os.path.join(script_dir, 'app', 'static', 'uploads')
    check_directory(app_uploads)
    
    # Check the temporary directory
    temp_dir = tempfile.gettempdir()
    check_directory(temp_dir)
    
    # Print permissions
    print("\nDirectory permissions:")
    for directory in [main_uploads, app_uploads]:
        if os.path.exists(directory):
            try:
                permissions = oct(os.stat(directory).st_mode)[-3:]
                owner = os.stat(directory).st_uid
                group = os.stat(directory).st_gid
                print(f"{directory}: permissions={permissions}, owner={owner}, group={group}")
            except Exception as e:
                print(f"Could not get permissions for {directory}: {str(e)}")

if __name__ == "__main__":
    main() 