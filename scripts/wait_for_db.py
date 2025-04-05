#!/usr/bin/env python3
"""
Script to wait for MySQL database to be ready.
Useful in Docker environments where the database service might start up slower than the application.
"""

import os
import sys
import time
import mysql.connector
from mysql.connector import Error

# Add parent directory to path to allow importing from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.core.db_utils import get_db_connection, get_db_config
except ImportError:
    print("Could not import from app.core.db_utils, falling back to local implementation")
    
    def get_db_config():
        return {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'root'),
            'database': os.environ.get('MYSQL_DATABASE', 'music_analyzer')
        }

def wait_for_db(max_attempts=30, delay=2):
    """
    Wait for the MySQL database to be ready.
    
    Args:
        max_attempts: Maximum number of connection attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if connection succeeded, False otherwise
    """
    config = get_db_config()
    host = config['host']
    port = config['port']
    user = config['user']
    password = config['password']
    database = config['database']
    
    print(f"Waiting for MySQL database at {host}:{port}...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            # Connect without specifying the database in case it doesn't exist yet
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            
            if connection.is_connected():
                print(f"Successfully connected to MySQL!")
                
                # Check if database exists, create if not
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                cursor.close()
                
                connection.close()
                return True
        except Error as e:
            print(f"Connection failed: {e}")
            if attempt < max_attempts:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    print("Maximum connection attempts reached. Could not connect to MySQL.")
    return False

if __name__ == "__main__":
    success = wait_for_db()
    sys.exit(0 if success else 1) 