#!/usr/bin/env python3
"""
Check if the app structure is correct and help diagnose import issues.
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and print the result."""
    exists = os.path.isfile(path)
    print(f"{description}: {'✅ Found' if exists else '❌ Not found'} at {path}")
    return exists

def check_dir_exists(path, description):
    """Check if a directory exists and print the result."""
    exists = os.path.isdir(path)
    print(f"{description}: {'✅ Found' if exists else '❌ Not found'} at {path}")
    return exists

def check_module_importable(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"Module '{module_name}': ✅ Importable")
        return True
    except ImportError as e:
        print(f"Module '{module_name}': ❌ Not importable - {str(e)}")
        return False

def main():
    """Main function to check app structure."""
    print("Checking Mix Analyzer app structure...\n")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}\n")
    
    # Check main app files
    print("Checking main app files:")
    app_py = os.path.join(current_dir, "app.py")
    check_file_exists(app_py, "Main app.py file")
    
    # Check app directory
    print("\nChecking app directory:")
    app_dir = os.path.join(current_dir, "app")
    app_dir_exists = check_dir_exists(app_dir, "App directory")
    
    if app_dir_exists:
        # Check key files in app directory
        audio_analyzer_py = os.path.join(app_dir, "audio_analyzer.py")
        check_file_exists(audio_analyzer_py, "audio_analyzer.py")
        
        openai_analyzer_py = os.path.join(app_dir, "openai_analyzer.py")
        check_file_exists(openai_analyzer_py, "openai_analyzer.py")
        
        # Check templates and static directories
        templates_dir = os.path.join(app_dir, "templates")
        check_dir_exists(templates_dir, "Templates directory")
        
        static_dir = os.path.join(app_dir, "static")
        static_dir_exists = check_dir_exists(static_dir, "Static directory")
        
        if static_dir_exists:
            uploads_dir = os.path.join(static_dir, "uploads")
            check_dir_exists(uploads_dir, "Uploads directory")
    
    # Check if app is in Python path
    print("\nChecking Python path:")
    in_python_path = current_dir in sys.path
    print(f"Current directory in Python path: {'✅ Yes' if in_python_path else '❌ No'}")
    
    if not in_python_path:
        print("Adding current directory to Python path...")
        sys.path.insert(0, current_dir)
        print("Current directory added to Python path.")
    
    # Try importing app modules
    print("\nTrying to import app modules:")
    try:
        import app.audio_analyzer
        print("✅ Successfully imported app.audio_analyzer")
    except ImportError as e:
        print(f"❌ Failed to import app.audio_analyzer: {str(e)}")
        print("\nPossible solutions:")
        print("1. Make sure you're running this script from the project root directory")
        print("2. Make sure the app directory contains an __init__.py file")
        print("3. Try running with: PYTHONPATH=. python app.py")
    
    # Check for __init__.py
    init_py = os.path.join(app_dir, "__init__.py")
    init_exists = check_file_exists(init_py, "\nApp __init__.py file")
    
    if not init_exists and app_dir_exists:
        print("\nCreating __init__.py file in app directory...")
        try:
            with open(init_py, 'w') as f:
                f.write("# This file makes the app directory a Python package\n")
            print("✅ Created __init__.py file")
        except Exception as e:
            print(f"❌ Failed to create __init__.py file: {str(e)}")

if __name__ == "__main__":
    main() 