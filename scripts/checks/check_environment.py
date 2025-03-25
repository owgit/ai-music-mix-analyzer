#!/usr/bin/env python3
"""
Environment Checker for Mix Analyzer

This script checks if your environment is properly set up to run the Mix Analyzer application.
It verifies Python version, required packages, and system dependencies.
"""

import sys
import os
import platform
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print(f"Python version: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        return False
    
    if sys.version_info >= (3, 12):
        print("⚠️ Python 3.12+ detected. Some packages might have compatibility issues.")
        print("   Consider using Python 3.10 or 3.11 for best compatibility.")
        return True
    
    print("✅ Python version is compatible.")
    return True

def check_package(package_name):
    """Check if a package is installed and get its version."""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} is not installed.")
        return False
    
    try:
        package = importlib.import_module(package_name)
        version = getattr(package, "__version__", "unknown")
        print(f"✅ {package_name} is installed (version: {version}).")
        return True
    except ImportError:
        print(f"❌ {package_name} is installed but cannot be imported.")
        return False

def check_system_dependencies():
    """Check system dependencies based on the operating system."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("\nChecking macOS dependencies:")
        
        # Check for Apple Silicon
        is_apple_silicon = platform.machine() == "arm64"
        if is_apple_silicon:
            print("ℹ️ Detected Apple Silicon (M1/M2/M3) Mac.")
            print("   Some packages might have build issues on this architecture.")
            
            # Check if running under Rosetta 2
            try:
                result = subprocess.run(["arch"], capture_output=True, text=True)
                if "i386" in result.stdout or "x86_64" in result.stdout:
                    print("✅ Running under Rosetta 2, which can help with compatibility.")
                else:
                    print("ℹ️ Running natively on ARM. If you encounter issues, consider using Rosetta 2.")
            except FileNotFoundError:
                print("ℹ️ Could not determine if running under Rosetta 2.")
        
        try:
            result = subprocess.run(["brew", "--version"], capture_output=True, text=True)
            print("✅ Homebrew is installed.")
            
            # Check for libsndfile
            result = subprocess.run(["brew", "list", "libsndfile"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ libsndfile is installed.")
            else:
                print("⚠️ libsndfile might not be installed. Install with: brew install libsndfile")
        except FileNotFoundError:
            print("⚠️ Homebrew not found. Consider installing it for managing dependencies.")
    
    elif system == "Linux":
        print("\nChecking Linux dependencies:")
        try:
            # Check for libsndfile
            result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
            if "libsndfile.so" in result.stdout:
                print("✅ libsndfile is installed.")
            else:
                print("⚠️ libsndfile might not be installed. Install with: sudo apt-get install libsndfile1")
            
            # Check for ffmpeg
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ ffmpeg is installed.")
            else:
                print("⚠️ ffmpeg might not be installed. Install with: sudo apt-get install ffmpeg")
        except FileNotFoundError:
            print("⚠️ Some system checks failed. Make sure libsndfile1 and ffmpeg are installed.")
    
    elif system == "Windows":
        print("\nChecking Windows dependencies:")
        # Windows-specific checks could go here
        print("ℹ️ On Windows, you might need the Visual C++ Redistributable if you encounter DLL errors.")
        print("   Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe")

def check_openai_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
            if "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content:
                print("✅ OpenAI API key is set in .env file.")
                return True
    
    if api_key:
        print("✅ OpenAI API key is set in environment variables.")
        return True
    else:
        print("⚠️ OpenAI API key is not set. AI insights will not be available.")
        print("   Set your API key in the .env file or as an environment variable.")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Mix Analyzer Environment Checker")
    print("=" * 60)
    
    # System information
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    python_ok = check_python_version()
    
    print("\nChecking required packages:")
    packages = ["flask", "numpy", "scipy", "librosa", "matplotlib", "pydub", "openai"]
    package_status = [check_package(pkg) for pkg in packages]
    
    check_system_dependencies()
    
    print("\nChecking OpenAI API key:")
    api_key_ok = check_openai_api_key()
    
    print("\n" + "=" * 60)
    print("Summary:")
    if all(package_status) and python_ok:
        print("✅ Your environment is ready to run Mix Analyzer!")
        if not api_key_ok:
            print("⚠️ Note: OpenAI API key is not set. AI insights will not be available.")
    else:
        print("⚠️ Some issues were detected. Please fix them before running Mix Analyzer.")
        print("   See TROUBLESHOOTING.md for more information.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 