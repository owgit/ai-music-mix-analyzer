#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def main():
    print("Setting up Mix Analyzer...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    # Warning for Python 3.12
    if python_version.major == 3 and python_version.minor >= 12:
        print("Note: You're using Python 3.12+. Some packages might have compatibility issues.")
        print("If you encounter problems, consider using Python 3.10 or 3.11 instead.")
    
    # Check for Apple Silicon
    is_apple_silicon = platform.system() == "Darwin" and platform.machine() == "arm64"
    if is_apple_silicon:
        print("Detected Apple Silicon (M1/M2/M3) Mac.")
        print("Using special installation procedure for compatibility.")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Determine the pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Upgrade pip and install setuptools first
    print("Upgrading pip and installing setuptools...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"])
    subprocess.run([pip_path, "install", "--upgrade", "setuptools>=65.5.0", "wheel"])
    
    # Install NumPy and SciPy first (to avoid dependency issues)
    print("Installing NumPy and SciPy...")
    subprocess.run([pip_path, "install", "numpy>=1.26.0", "scipy>=1.11.3"])
    
    # Install matplotlib separately with special handling for Apple Silicon
    print("Installing matplotlib...")
    if is_apple_silicon:
        # Use --only-binary to avoid building from source on Apple Silicon
        subprocess.run([pip_path, "install", "--only-binary=:all:", "matplotlib>=3.8.0"])
    else:
        subprocess.run([pip_path, "install", "matplotlib>=3.8.0"])
    
    # Install remaining dependencies
    print("Installing remaining dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    # Create uploads directory
    uploads_dir = os.path.join("app", "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        shutil.copy(env_example, env_file)
        print("Please edit the .env file to add your OpenAI API key if you want AI insights.")
    
    print("\nSetup complete!")
    print("\nTo run the application:")
    
    if os.name == 'nt':  # Windows
        print("1. Activate the virtual environment: venv\\Scripts\\activate")
        print("2. Run the app: python app.py")
    else:  # Unix/Linux/Mac
        print("1. Activate the virtual environment: source venv/bin/activate")
        print("2. Run the app: python app.py")
    
    print("\nThen open your browser and navigate to http://localhost:5000")

if __name__ == "__main__":
    main() 