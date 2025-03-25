# Environment Configuration Guide

This document explains how environment variables are managed in the Music Mix Analyzer project.

## Environment File Structure

The project uses a structured approach to environment variables:

### 1. Root `.env` File

The primary source of all configuration variables is the `.env` file in the project root directory. This file contains:

- API keys
- Model settings
- Security keys
- Application settings

This file is used by both standard and Docker installations, providing a single source of truth for most configuration settings.

### 2. Docker-specific Settings

Docker-specific environment settings are stored in `config/docker/.env`. This file only contains:

- Settings that are specific to Docker deployment
- Overrides for the root `.env` variables when running in Docker
- Docker-specific paths and resource constraints

### 3. Local Docker Overrides

For local Docker installations, you can create a `docker-compose.override.yml` file (from the provided example) to add custom overrides for your specific environment.

## Setting Up Your Environment

### Initial Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:
   ```bash
   # Replace with your actual API key
   OPENAI_API_KEY=your_api_key_here
   ```

3. Generate a secure secret key for your Flask application:
   ```bash
   python scripts/generate_secret_key.py --update-env
   ```

### Docker Setup

1. The `config/docker/.env` file should already contain appropriate defaults for Docker deployment

2. If you need to customize your Docker environment:
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

3. Edit `docker-compose.override.yml` with your specific overrides

## Environment Variable Precedence

When the application loads environment variables, it follows this precedence order (highest to lowest):

1. Variables explicitly set in the environment (e.g., via command line or Docker Compose)
2. Variables in `docker-compose.override.yml` (Docker only)
3. Variables in `config/docker/.env` (Docker only)
4. Variables in the root `.env` file
5. Default values hardcoded in the application

## Model Configuration

### Selecting AI Provider

You can choose between two AI providers:

```
# Options: "openai" or "openrouter"
AI_PROVIDER=openai
```

### Configuring OpenAI Models

When using OpenAI (AI_PROVIDER=openai), select your preferred model:

```
OPENAI_MODEL=gpt-4o-mini
```

Options include:
- gpt-4o-2024-11-20 (Latest version with enhanced creative writing)
- gpt-4o-2024-08-06 (Previous GPT-4o version)
- gpt-4o-mini (Fast, cost-effective model, good GPT-3.5 replacement)
- gpt-4-turbo-2024-04-09 (Latest GPT-4 Turbo with vision capabilities)
- gpt-3.5-turbo (Cost-effective for simpler tasks)

### Configuring OpenRouter Models

When using OpenRouter (AI_PROVIDER=openrouter), select your preferred model:

```
OPENROUTER_MODEL=anthropic/claude-3-haiku-20240307
```

Common options include:
- anthropic/claude-3-opus-20240229
- anthropic/claude-3-sonnet-20240229
- anthropic/claude-3-haiku-20240307
- google/gemini-1.5-pro-latest
- meta-llama/llama-3-70b-instruct

## Securing Environment Files

To prevent accidentally committing API keys and secrets to version control:

1. Run the sanitization script before committing changes:
   ```bash
   python scripts/sanitize_env.py
   ```

2. This script automatically removes sensitive information from environment files

3. Always check for sensitive information in your git diff before committing

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| **API Keys** |  |  |  |
| `OPENAI_API_KEY` | Your OpenAI API key | None | Yes (if using OpenAI) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | None | Yes (if using OpenRouter) |
| **Model Configuration** |  |  |  |
| `AI_PROVIDER` | Which AI provider to use | "openai" | Yes |
| `OPENAI_MODEL` | OpenAI model to use | "gpt-4o-mini" | Yes (if using OpenAI) |
| `OPENROUTER_MODEL` | OpenRouter model to use | "anthropic/claude-3-haiku-20240307" | Yes (if using OpenRouter) |
| **Security** |  |  |  |
| `API_KEY` | Internal API authentication key | None | Yes |
| `SECRET_KEY` | Flask secret key | None | Yes |
| `FLASK_ENV` | Environment mode | "development" | Yes |
| **Analytics** |  |  |  |
| `ENABLE_ANALYTICS` | Enable analytics tracking | "false" | No |
| `MATOMO_URL` | Analytics platform URL | None | No |
| `MATOMO_SITE_ID` | Analytics site ID | None | No |
| **Docker Configuration** |  |  |  |
| `DATA_VOLUME` | Docker data volume path | "/data" | Docker only |
| `UPLOAD_FOLDER` | Docker uploads folder | "/uploads" | Docker only |
| `MAX_UPLOAD_SIZE_MB` | Maximum upload size | 20 | Docker only | 