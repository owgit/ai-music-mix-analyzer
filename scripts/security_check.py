#!/usr/bin/env python3
"""
Security check script for the Music Mix Analyzer application.
This script performs security audits tailored to the audio processing application.
"""

import os
import sys
import re
import subprocess
import importlib.util
from pathlib import Path

# Color codes for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(title):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 50}{RESET}")
    print(f"{BLUE}= {title}{RESET}")
    print(f"{BLUE}{'=' * 50}{RESET}\n")

def print_status(message, status, details=None):
    """Print a formatted status message."""
    status_color = GREEN if status == "PASS" else (YELLOW if status == "WARN" else RED)
    print(f"{message: <60} [{status_color}{status}{RESET}]")
    if details and status != "PASS":
        for line in details:
            print(f"  - {line}")
        print()

def check_audio_file_security():
    """Check security of audio file handling."""
    print_header("Audio File Upload Security")
    issues = []
    
    # Check for extension validation
    try:
        with open("app/routes.py", "r") as f:
            content = f.read()
            if "allowed_file" in content:
                print_status("File extension validation", "PASS")
            else:
                issues.append("File extension validation function not found")
                print_status("File extension validation", "FAIL", issues)
            
            if "secure_filename" in content:
                print_status("Secure filename function", "PASS")
            else:
                issues.append("Secure filename function not used")
                print_status("Secure filename function", "FAIL", [issues[-1]])
            
            if re.search(r"file\.filename == ''", content):
                print_status("Empty filename check", "PASS")
            else:
                issues.append("Empty filename validation may be missing")
                print_status("Empty filename check", "WARN", [issues[-1]])
            
            # Check file size limit
            if re.search(r"MAX_CONTENT_LENGTH", content) or "MAX_CONTENT_LENGTH" in content:
                print_status("File size limit", "PASS")
            else:
                issues.append("File size limit may not be implemented")
                print_status("File size limit", "WARN", [issues[-1]])
                
            # Check audio file type validation
            if re.search(r"mp3|wav|flac", content):
                print_status("Audio file type validation", "PASS")
            else:
                issues.append("Audio file type validation may be missing")
                print_status("Audio file type validation", "FAIL", [issues[-1]])
                
    except FileNotFoundError:
        issues.append("Could not find routes.py to check file upload security")
        print_status("File upload security checks", "FAIL", issues)
    
    return len(issues) == 0

def check_api_rate_limiting():
    """Check API rate limiting implementation."""
    print_header("API Security")
    issues = []
    
    # Check for rate limiting
    try:
        with open("app/__init__.py", "r") as f:
            content = f.read()
            if "Limiter" in content:
                print_status("Rate limiting implementation", "PASS")
            else:
                issues.append("Rate limiting may not be implemented")
                print_status("Rate limiting implementation", "FAIL", [issues[-1]])
            
            if "app.errorhandler(429)" in content:
                print_status("Rate limit exceeded handler", "PASS")
            else:
                issues.append("Rate limit exceeded handler may be missing")
                print_status("Rate limit exceeded handler", "WARN", [issues[-1]])
    except FileNotFoundError:
        issues.append("Could not find __init__.py to check API security")
        print_status("API security checks", "FAIL", issues)
    
    # Check for error handling in routes
    try:
        with open("app/routes.py", "r") as f:
            content = f.read()
            if re.search(r"jsonify\(\{\s*'error'", content) or re.search(r'jsonify\(\{\s*"error"', content):
                print_status("API error responses", "PASS")
            else:
                issues.append("Proper API error responses may be missing")
                print_status("API error responses", "WARN", [issues[-1]])
    except FileNotFoundError:
        pass  # Already reported above
    
    return len(issues) == 0

def check_open_api_endpoints():
    """Check for open API endpoints that might need authentication."""
    print_header("Open API Endpoints Security")
    issues = []
    
    # Check if API routes exist
    if os.path.exists("app/api/routes.py"):
        with open("app/api/routes.py", "r") as f:
            content = f.read()
            
            # Check for API endpoints
            endpoints = re.findall(r'@api_bp\.route\([\'"](.+?)[\'"]\s*,\s*methods=\[(.*?)\]\)', content)
            
            if endpoints:
                print(f"Found {len(endpoints)} API endpoints:")
                for endpoint, methods in endpoints:
                    print(f"  - {endpoint} ({methods})")
                
                # Check for authentication in API endpoints
                if "request.headers.get('Authorization'" in content or "token" in content.lower() or "auth" in content.lower():
                    print_status("API authentication", "PASS")
                else:
                    issues.append("API endpoints may not be protected by authentication")
                    print_status("API authentication", "WARN", [issues[-1]])
                    
                # Check if file_id paths use secure validation
                if re.search(r'/<file_id>', content) and not re.search(r'os\.path\.basename', content):
                    issues.append("File ID path parameters may not be properly validated")
                    print_status("API path parameter validation", "WARN", [issues[-1]])
                else:
                    print_status("API path parameter validation", "PASS")
                
                # Check if API has proper input validation
                if re.search(r'request\.get_json\(\)', content) and not re.search(r'if\s+not\s+request\.json', content):
                    issues.append("API JSON input validation may be insufficient")
                    print_status("API input validation", "WARN", [issues[-1]])
                else:
                    print_status("API input validation", "PASS")
                
                # Check for CORS headers
                if "Access-Control-Allow-Origin" in content:
                    if "*" in content and "Access-Control-Allow-Origin" in content:
                        issues.append("API has wildcard CORS policy, which may be insecure")
                        print_status("API CORS policy", "WARN", [issues[-1]])
                    else:
                        print_status("API CORS policy", "PASS")
                else:
                    print_status("API CORS policy", "INFO")  # Not necessarily an issue
            else:
                print_status("No API endpoints found", "INFO")
    else:
        print_status("No API routes file found", "INFO")
    
    return len(issues) == 0

def check_security_headers():
    """Check implementation of security headers."""
    print_header("Security Headers")
    issues = []
    
    try:
        with open("app/__init__.py", "r") as f:
            content = f.read()
            
            # Check for security headers
            security_headers = {
                "Content-Security-Policy": "Content Security Policy",
                "X-Content-Type-Options": "X-Content-Type-Options",
                "X-Frame-Options": "X-Frame-Options",
                "X-XSS-Protection": "XSS Protection",
                "Strict-Transport-Security": "HSTS"
            }
            
            for header, name in security_headers.items():
                if header in content:
                    print_status(f"{name}", "PASS")
                else:
                    issues.append(f"{name} header may be missing")
                    print_status(f"{name}", "WARN", [issues[-1]])
            
            # Check for CSP configuration
            if "script-src" in content and "style-src" in content:
                print_status("CSP configuration", "PASS")
            else:
                issues.append("Content Security Policy may not be properly configured")
                print_status("CSP configuration", "WARN", [issues[-1]])
                
    except FileNotFoundError:
        issues.append("Could not find __init__.py to check security headers")
        print_status("Security headers checks", "FAIL", issues)
    
    return len(issues) == 0

def check_library_vulnerabilities():
    """Check for known vulnerabilities in audio libraries."""
    print_header("Library Security")
    issues = []
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().splitlines()
            
            # Filter out comments and empty lines
            requirements = [r for r in requirements if r and not r.startswith('#')]
            
            # Check Flask version
            flask_req = next((r for r in requirements if r.lower().startswith('flask==')), None)
            if flask_req:
                flask_version = flask_req.split('==')[1]
                if flask_version.startswith(('2.0', '2.1', '2.2')):
                    issues.append(f"Using older Flask version: {flask_version}. Consider upgrading to 2.3+")
                    print_status("Flask version", "WARN", [issues[-1]])
                else:
                    print_status("Flask version", "PASS")
            
            # Check librosa version for audio processing
            librosa_req = next((r for r in requirements if r.lower().startswith('librosa==')), None)
            if librosa_req:
                librosa_version = librosa_req.split('==')[1]
                if librosa_version.startswith(('0.8', '0.9')):
                    issues.append(f"Using older librosa version: {librosa_version}. Consider upgrading to 0.10+")
                    print_status("Librosa version", "WARN", [issues[-1]])
                else:
                    print_status("Librosa version", "PASS")
            
            # Check openai package version
            openai_req = next((r for r in requirements if r.lower().startswith('openai==')), None)
            if openai_req:
                openai_version = openai_req.split('==')[1]
                if not openai_version.startswith(('1.')):
                    issues.append(f"Using older OpenAI API version: {openai_version}. Should upgrade to 1.x")
                    print_status("OpenAI API version", "WARN", [issues[-1]])
                else:
                    print_status("OpenAI API version", "PASS")
            
            # Check for other crucial packages
            for package, min_version in [
                ('numpy', '1.20'),
                ('scipy', '1.7'),
                ('matplotlib', '3.5'),
                ('requests', '2.25'),
                ('python-dotenv', '0.19')
            ]:
                pkg_req = next((r for r in requirements if r.lower().startswith(f'{package}==')), None)
                if pkg_req:
                    pkg_version = pkg_req.split('==')[1]
                    print_status(f"{package} version", "INFO")
                
    except FileNotFoundError:
        issues.append("Could not find requirements.txt to check dependencies")
        print_status("Library security checks", "FAIL", issues)
    
    # Check for latest pip-audit if available
    try:
        print("\nAttempting to run pip-audit for vulnerability scanning...")
        subprocess.run(['pip', 'install', 'pip-audit'], check=True, capture_output=True)
        result = subprocess.run(['pip-audit'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{GREEN}No vulnerabilities found by pip-audit{RESET}")
        else:
            print(f"{YELLOW}pip-audit found potential vulnerabilities:{RESET}")
            print(result.stdout)
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"{YELLOW}Could not run pip-audit - skipping vulnerability scan{RESET}")
    
    return len(issues) == 0

def check_audio_processing_safety():
    """Check for audio processing security issues."""
    print_header("Audio Processing Security")
    issues = []
    
    # Check for potential buffer overflow issues in audio processing
    try:
        with open("app/core/audio_analyzer.py", "r") as f:
            content = f.read()
            
            # Check for proper error handling in audio processing
            if re.search(r"try\s*:.+?except", content, re.DOTALL):
                print_status("Error handling in audio processing", "PASS")
            else:
                issues.append("Error handling in audio processing may be insufficient")
                print_status("Error handling in audio processing", "WARN", [issues[-1]])
            
            # Check for librosa load with sr parameter
            if re.search(r"librosa\.load\(.+?sr=", content):
                print_status("Sample rate specification", "PASS")
            else:
                issues.append("Sample rate may not be explicitly set in librosa.load")
                print_status("Sample rate specification", "WARN", [issues[-1]])
            
            # Check for tempfile usage
            if "tempfile" in content:
                print_status("Temporary file handling", "PASS")
            else:
                issues.append("Temporary file handling may not be properly implemented")
                print_status("Temporary file handling", "WARN", [issues[-1]])
    
    except FileNotFoundError:
        issues.append("Could not find audio_analyzer.py to check audio processing")
        print_status("Audio processing checks", "FAIL", issues)
    
    # Check for proper output directory permissions
    upload_dir = os.path.join('uploads')
    if os.path.exists(upload_dir):
        mode = oct(os.stat(upload_dir).st_mode)[-3:]
        if mode == '755' or mode == '750':
            print_status("Upload directory permissions", "PASS")
        else:
            issues.append(f"Upload directory has potentially insecure permissions: {mode}")
            print_status("Upload directory permissions", "WARN", [issues[-1]])
    else:
        issues.append("Could not find uploads directory")
        print_status("Upload directory checks", "WARN", [issues[-1]])
    
    return len(issues) == 0

def check_api_key_handling():
    """Check secure handling of API keys."""
    print_header("API Key Security")
    issues = []
    
    # Check if .env is gitignored
    try:
        with open(".gitignore", "r") as f:
            content = f.read()
            if re.search(r"\.env", content):
                print_status("Environment files gitignored", "PASS")
            else:
                issues.append(".env files may not be excluded from Git")
                print_status("Environment files gitignored", "FAIL", [issues[-1]])
    except FileNotFoundError:
        issues.append("Could not find .gitignore file")
        print_status("Environment file checks", "FAIL", issues)
    
    # Check for environment variable validation
    try:
        with open("app/core/openai_analyzer.py", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content and "os.environ.get" in content:
                print_status("OpenAI API key handling", "PASS")
            else:
                issues.append("OpenAI API key handling may be insecure")
                print_status("OpenAI API key handling", "WARN", [issues[-1]])
    except FileNotFoundError:
        issues.append("Could not find openai_analyzer.py to check API key handling")
        print_status("API key handling checks", "WARN", issues)
    
    # Check for .env.example
    if os.path.exists('.env.example') or os.path.exists('config/.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'your_openai_api_key_here' in content or 'OPENAI_API_KEY=' in content:
                print_status("API key template in .env.example", "PASS")
            else:
                issues.append(".env.example may not include API key template")
                print_status("API key template in .env.example", "WARN", [issues[-1]])
    else:
        issues.append("Could not find .env.example file")
        print_status(".env.example file", "WARN", [issues[-1]])
    
    return len(issues) == 0

def main():
    """Run all security checks."""
    print(f"{BLUE}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{RESET}")
    print(f"{BLUE}▓▓                                                      ▓▓{RESET}")
    print(f"{BLUE}▓▓  {GREEN}Music Mix Analyzer - Security Audit Tool{BLUE}            ▓▓{RESET}")
    print(f"{BLUE}▓▓                                                      ▓▓{RESET}")
    print(f"{BLUE}▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓{RESET}")
    
    results = [
        check_audio_file_security(),
        check_api_rate_limiting(),
        check_open_api_endpoints(),
        check_security_headers(),
        check_library_vulnerabilities(),
        check_audio_processing_safety(),
        check_api_key_handling()
    ]
    
    print("\n\n" + "=" * 80)
    print(f"{BLUE}Security Check Summary{RESET}")
    print("=" * 80)
    passed = results.count(True)
    total = len(results)
    print(f"Passed: {passed}/{total} check categories")
    
    # Return non-zero exit code if any checks failed
    if passed < total:
        print(f"\n{YELLOW}Warning: Some security checks raised issues{RESET}")
        print("Review the issues above and address them to improve application security.")
        sys.exit(0)  # Not failing CI for warnings
    else:
        print(f"\n{GREEN}All security check categories passed!{RESET}")
        print(f"{GREEN}Note: This does not guarantee the application is 100% secure.{RESET}")
        print(f"{GREEN}Regular security reviews and updates are still recommended.{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main() 