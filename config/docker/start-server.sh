#!/bin/bash

# Get the user and group ID of the current user
HOST_UID=$(id -u)
HOST_GID=$(id -g)

# Export them as environment variables
export HOST_UID
export HOST_GID

echo "Starting containers with UID:GID = $HOST_UID:$HOST_GID"

# Navigate to the project root directory
cd "$(dirname "$0")/../.." || exit

# Start the containers with the correct user permissions
docker-compose -f config/docker/docker-compose.yml up -d

echo "Containers started. Check logs with: docker-compose -f config/docker/docker-compose.yml logs -f" 