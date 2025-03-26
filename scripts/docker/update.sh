#!/bin/bash
# Mix Analyzer - Docker Update Script

# Change to the project root directory
cd "$(dirname "$0")/../.."
PROJECT_ROOT=$(pwd)
echo "Project root: $PROJECT_ROOT"

echo "Updating Mix Analyzer from Git..."

# Pull latest changes
echo "Pulling latest changes..."
git pull

# Check if pull was successful
if [ $? -ne 0 ]; then
    echo "Error: Git pull failed. Aborting update."
    exit 1
fi

# Ensure config directory exists
mkdir -p config/docker

echo "Rebuilding Docker containers..."
docker-compose build

echo "Restarting Docker containers..."
docker-compose down
docker-compose up -d

echo "Update completed successfully!"
echo "To view logs, run: docker-compose logs -f" 