#!/usr/bin/env python
"""
Script to generate a secure random key for Flask applications.
This script will generate a random secret key and optionally update the .env file.
"""

import secrets
import os
import argparse

def generate_secret_key(length=32):
    """Generate a secure random key"""
    return secrets.token_hex(length)

def update_env_file(key):
    """Update the SECRET_KEY in the .env file"""
    env_path = '.env'
    
    # Check if .env exists, if not create from example
    if not os.path.exists(env_path):
        if os.path.exists('.env.example'):
            print("Creating .env from .env.example")
            with open('.env.example', 'r') as example:
                with open(env_path, 'w') as env:
                    env.write(example.read())
        else:
            print("Creating new .env file")
            with open(env_path, 'w') as env:
                env.write("# Mix Analyzer Environment Variables\n\n")
                env.write("# OpenAI API Key (required for AI insights)\n")
                env.write("OPENAI_API_KEY=\n\n")
                env.write("# Flask Configuration\n")
                env.write("FLASK_APP=app.py\n")
                env.write("FLASK_ENV=development\n")
    
    # Read the content of the .env file
    with open(env_path, 'r') as f:
        env_content = f.read()
        
    # Check if SECRET_KEY already exists
    if 'SECRET_KEY=' in env_content:
        # Replace existing SECRET_KEY
        lines = []
        for line in env_content.split('\n'):
            if line.startswith('SECRET_KEY='):
                lines.append(f'SECRET_KEY={key}')
            else:
                lines.append(line)
        
        new_content = '\n'.join(lines)
    else:
        # Add SECRET_KEY to the end
        new_content = env_content.rstrip() + f'\n\n# Secure random key for Flask sessions\nSECRET_KEY={key}\n'
    
    # Write the updated content back to the .env file
    with open(env_path, 'w') as f:
        f.write(new_content)
        
    print(f"Updated SECRET_KEY in {env_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a secure secret key")
    parser.add_argument("-l", "--length", type=int, default=32, help="Length of the key in bytes")
    parser.add_argument("-u", "--update-env", action="store_true", help="Update .env file with the generated key")
    args = parser.parse_args()
    
    # Generate a secret key
    key = generate_secret_key(args.length)
    print(f"Generated SECRET_KEY: {key}")
    
    # Update .env file if requested
    if args.update_env:
        update_env_file(key)
    else:
        print("\nTo add this key to your .env file, run:")
        print(f"python {os.path.basename(__file__)} --update-env")
        print("\nOr manually add this line to your .env file:")
        print(f"SECRET_KEY={key}") 