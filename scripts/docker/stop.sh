#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

echo -e "${YELLOW}Music Mix Analyzer - Docker Shutdown${NC}"
echo "----------------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if the container is running
if ! docker ps | grep -q music-analyzer; then
    echo -e "${YELLOW}Music Analyzer is not running.${NC}"
    exit 0
fi

# Change to the project root directory
cd "$PROJECT_ROOT"

# Stop the container
echo -e "${YELLOW}Stopping the Docker container...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" down

# Check if the container stopped successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Music Analyzer has been stopped.${NC}"
else
    echo -e "${RED}Failed to stop the Docker container.${NC}"
    echo "Try to stop it manually: docker stop music-analyzer"
fi 