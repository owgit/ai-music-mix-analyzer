#!/bin/bash
# Mix Analyzer - Docker Update Script
set -e

# Function to detect environment
detect_environment() {
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "local"
    elif [[ -d "/home/mixanalytic" ]]; then
        echo "production"
    else
        echo "unknown"
    fi
}

# Function to find project root
find_project_root() {
    local current_dir="$PWD"
    while [[ "$current_dir" != "/" ]]; do
        if [[ -f "$current_dir/requirements.txt" ]] || [[ -d "$current_dir/.git" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done
    
    # If we couldn't find it by traversing up, try using git
    local git_root="$(git rev-parse --show-toplevel 2>/dev/null)"
    if [[ -n "$git_root" ]]; then
        echo "$git_root"
        return 0
    fi
    
    # If still not found, try Sites/music
    if [[ -d "$HOME/Sites/music" ]]; then
        echo "$HOME/Sites/music"
        return 0
    fi
    
    return 1
}

# Find the project root first
PROJECT_ROOT=$(find_project_root)
if [[ $? -ne 0 ]]; then
    echo "Error: Could not determine project root directory!"
    echo "Please run this script from within the project directory."
    exit 1
fi

# Change to the project root directory
cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"
echo "Environment: $(detect_environment)"

# Check for requirements.txt
if [[ ! -f "requirements.txt" ]]; then
    echo "Error: requirements.txt not found in project root!"
    echo "Checking alternative locations..."
    
    # Try to find requirements.txt in common locations
    if [[ -f "$HOME/Sites/music/requirements.txt" ]]; then
        echo "Found in ~/Sites/music, copying..."
        cp "$HOME/Sites/music/requirements.txt" .
    elif [[ -f "$(git rev-parse --show-toplevel 2>/dev/null)/requirements.txt" ]]; then
        echo "Found in git root, copying..."
        cp "$(git rev-parse --show-toplevel)/requirements.txt" .
    else
        echo "Could not find requirements.txt in any location."
        exit 1
    fi
fi

echo "Using requirements.txt from: $PROJECT_ROOT/requirements.txt"

echo "Updating Mix Analyzer from Git..."

# Pull latest changes
echo "Pulling latest changes..."
git pull

# Check if pull was successful
if [[ $? -ne 0 ]]; then
    echo "Error: Git pull failed. Aborting update."
    exit 1
fi

# Ensure config directory exists
mkdir -p config/docker

# Stop and rebuild containers
echo "Stopping and rebuilding containers..."
docker-compose down --remove-orphans
docker-compose build

# Start containers with environment variables fixes
echo "Starting containers with fixes for caching issues..."
docker-compose up -d

# Create cache directories with proper permissions
echo "Creating cache directories with proper permissions..."
docker exec music-analyzer mkdir -p /tmp/matplotlib /tmp/numba_cache
docker exec music-analyzer chmod 777 /tmp/matplotlib /tmp/numba_cache

# Check status
echo "Container status:"
docker-compose ps

echo "Update completed!" 