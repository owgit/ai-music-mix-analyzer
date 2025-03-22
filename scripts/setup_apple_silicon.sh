#!/bin/bash
# Setup script for Mix Analyzer on Apple Silicon Macs using Rosetta 2

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "This script is only for macOS systems."
    exit 1
fi

# Check if running on Apple Silicon
if [[ "$(uname -m)" != "arm64" ]]; then
    echo "This script is specifically for Apple Silicon (M1/M2/M3) Macs."
    exit 1
fi

echo "========================================================"
echo "Mix Analyzer Setup for Apple Silicon Macs"
echo "========================================================"

# Check if Rosetta 2 is installed
if ! /usr/bin/pgrep -q oahd; then
    echo "Installing Rosetta 2..."
    softwareupdate --install-rosetta --agree-to-license
else
    echo "Rosetta 2 is already installed."
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create a virtual environment using x86_64 architecture
echo "Creating a virtual environment with x86_64 architecture..."
arch -x86_64 /usr/bin/python3 -m venv "$SCRIPT_DIR/venv_x86"

# Check if virtual environment was created successfully
if [ ! -d "$SCRIPT_DIR/venv_x86" ]; then
    echo "Failed to create virtual environment. Please check your Python installation."
    exit 1
fi

# Activate the virtual environment
echo "Activating virtual environment..."
if [ -f "$SCRIPT_DIR/venv_x86/bin/activate" ]; then
    source "$SCRIPT_DIR/venv_x86/bin/activate"
else
    echo "Virtual environment activation script not found. Installation failed."
    exit 1
fi

# Verify activation
if [[ "$VIRTUAL_ENV" != "$SCRIPT_DIR/venv_x86" ]]; then
    echo "Virtual environment activation failed. Please try manually:"
    echo "source $SCRIPT_DIR/venv_x86/bin/activate"
    exit 1
fi

echo "Virtual environment activated successfully."

# Upgrade pip and install setuptools
echo "Upgrading pip and installing setuptools..."
"$SCRIPT_DIR/venv_x86/bin/pip" install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
"$SCRIPT_DIR/venv_x86/bin/pip" install --only-binary=:all: numpy>=1.26.0 scipy>=1.11.3 matplotlib>=3.8.0
"$SCRIPT_DIR/venv_x86/bin/pip" install Flask==2.3.3 Werkzeug==2.3.7 pydub==0.25.1
"$SCRIPT_DIR/venv_x86/bin/pip" install librosa==0.10.1 openai>=1.0.0

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p "$SCRIPT_DIR/app/static/uploads"

# Create .env file if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    echo "Creating .env file from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "Please edit the .env file to add your OpenAI API key if you want AI insights."
fi

echo "========================================================"
echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source $SCRIPT_DIR/venv_x86/bin/activate"
echo "2. Run the app: python app.py"
echo ""
echo "Or simply use the run script: ./run.sh"
echo ""
echo "Then open your browser and navigate to http://localhost:5000"
echo "========================================================" 