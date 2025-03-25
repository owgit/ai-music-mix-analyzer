"""
Check scripts for verifying the Music Mix Analyzer configuration and security.
"""

# Import the main check function
from scripts.checks.check_project_consistency import main as check_project_consistency

__all__ = ['check_project_consistency'] 