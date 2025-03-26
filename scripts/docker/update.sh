#!/bin/bash
# Mix Analyzer - Docker Update Script

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

# Ensure .dockerignore is in root
if [[ ! -f ".dockerignore" ]] && [[ -f "config/docker/.dockerignore" ]]; then
    echo "Moving .dockerignore to root..."
    cp config/docker/.dockerignore .
    sed -i '' '/Dockerfile/d' .dockerignore 2>/dev/null || sed -i '/Dockerfile/d' .dockerignore
    sed -i '' '/docker-compose.yml/d' .dockerignore 2>/dev/null || sed -i '/docker-compose.yml/d' .dockerignore
fi

echo "Rebuilding Docker containers..."

# Stop and remove existing containers first
echo "Stopping and removing existing containers..."
docker-compose down --remove-orphans

# Remove existing container if it exists
if docker ps -a | grep -q "music-analyzer"; then
    echo "Removing existing music-analyzer container..."
    docker rm -f music-analyzer
fi

# Build and start containers
echo "Building fresh containers..."
docker-compose build

echo "Starting containers..."
docker-compose up -d

# Check if containers started successfully
if docker ps | grep -q "music-analyzer"; then
    echo "Update completed successfully!"
    echo "To view logs, run: docker-compose logs -f"
else
    echo "Error: Failed to start containers. Check logs for details."
    docker-compose logs
    exit 1
fi 