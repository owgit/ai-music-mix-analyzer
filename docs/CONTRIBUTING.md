# Contributing to Music Mix Analyzer

Thank you for considering contributing to Music Mix Analyzer! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list to see if the problem has already been reported. If it has and the issue is still open, add a comment to the existing issue instead of opening a new one.

When creating a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the issue
- Describe the behavior you observed after following the steps
- Explain what behavior you expected to see instead
- Include screenshots if possible
- Include details about your configuration (OS, browser, Python version, etc.)

### Suggesting Features

Feature suggestions are tracked as GitHub issues. When creating a feature request:

- Use a clear and descriptive title
- Provide a detailed description of the suggested feature
- Explain why this feature would be useful to most users
- Include screenshots or mockups if applicable

### Pull Requests

- Fill in the required template
- Follow the Python style guide (PEP 8)
- Include appropriate tests
- Update documentation as needed
- End all files with a newline
- Place imports in the following order:
  - Standard library imports
  - Related third-party imports
  - Local application imports

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Make your changes
6. Run tests
7. Submit a pull request

## Coding Conventions

- Follow PEP 8 style guide
- Use descriptive variable and function names
- Write docstrings for functions and classes
- Comment your code where necessary
- Keep functions and methods focused and small

## Git Workflow

1. Update your fork's main branch:
   ```bash
   git checkout main
   git pull upstream main
   ```
2. Create a new branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Commit with a descriptive message
5. Push to your fork
6. Create a pull request

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request

## Documentation

- Update the README.md if necessary
- Document new features, parameters, or significant changes
- Keep documentation up to date with changes

Thank you for contributing to Music Mix Analyzer! 