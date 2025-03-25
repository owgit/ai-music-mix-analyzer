#!/usr/bin/env python3
"""
Check if the audio_analyzer module can be imported correctly.
This script helps diagnose import issues.
"""

import os
import sys
import importlib

def check_import(module_name):
    """Try to import a module and print the result."""
    print(f"Trying to import {module_name}...")
    try:
        module = importlib.import_module(module_name)
        print(f"SUCCESS: Module {module_name} imported successfully")
        print(f"Module location: {module.__file__}")
        return True
    except ImportError as e:
        print(f"ERROR: Could not import {module_name}")
        print(f"Error message: {str(e)}")
        return False

def check_function_import(module_name, function_name):
    """Try to import a function from a module and print the result."""
    print(f"Trying to import {function_name} from {module_name}...")
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        print(f"SUCCESS: Function {function_name} imported successfully from {module_name}")
        return True
    except ImportError as e:
        print(f"ERROR: Could not import module {module_name}")
        print(f"Error message: {str(e)}")
        return False
    except AttributeError as e:
        print(f"ERROR: Module {module_name} does not have function {function_name}")
        print(f"Error message: {str(e)}")
        return False

def main():
    """Check imports for the Mix Analyzer application."""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Add the script directory to the path
    sys.path.append(script_dir)
    print(f"Python path: {sys.path}")
    
    # Check if app directory exists
    app_dir = os.path.join(script_dir, 'app')
    if os.path.exists(app_dir):
        print(f"App directory exists: {app_dir}")
    else:
        print(f"ERROR: App directory does not exist: {app_dir}")
        return
    
    # Check if __init__.py exists in app directory
    init_file = os.path.join(app_dir, '__init__.py')
    if os.path.exists(init_file):
        print(f"__init__.py exists in app directory: {init_file}")
    else:
        print(f"WARNING: __init__.py does not exist in app directory")
        print(f"Creating empty __init__.py file...")
        with open(init_file, 'w') as f:
            f.write("# This file makes the app directory a Python package\n")
    
    # Check imports
    modules_to_check = [
        'app',
        'app.audio_analyzer',
        'librosa',
        'pydub',
        'numpy',
        'matplotlib'
    ]
    
    for module in modules_to_check:
        check_import(module)
        print()
    
    # Check function imports
    function_imports = [
        ('app.audio_analyzer', 'analyze_mix')
    ]
    
    for module, function in function_imports:
        check_function_import(module, function)
        print()
    
    print("Import check complete")

if __name__ == "__main__":
    main() 