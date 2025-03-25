# Docker Configuration

Docker configuration files should be stored in this directory according to the project rules. However, for compatibility with standard Docker behavior, the following files are symlinked to the root directory:

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.override.yml`

When making changes to Docker configuration, always edit the files in this directory first, then update the symlinks if necessary.

## Directory Content

- `Dockerfile`: Main Docker image definition
- `docker-compose.yml`: Main Docker Compose configuration
- `.env`: Docker-specific environment variables
- `.dockerignore`: Files to exclude from Docker context 