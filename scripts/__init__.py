"""
Music Mix Analyzer Scripts Package
This package contains utility scripts for setup, maintenance, and checks.
"""

# Import common utilities for easy access
from scripts.utils.env_loader import load_environment
from scripts.utils.sanitize_env import sanitize_all_env_files

__all__ = ['load_environment', 'sanitize_all_env_files'] 