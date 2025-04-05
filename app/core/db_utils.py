"""
Centralized database utilities for the Music Mix Analyzer application.
All database connections should use these utilities for consistency.
"""

import os
import mysql.connector
from mysql.connector import Error

def get_db_config():
    """
    Get standardized database configuration from environment variables
    
    Returns:
        Dictionary with database connection parameters
    """
    return {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'root'),
        'database': os.environ.get('MYSQL_DATABASE', 'music_analyzer')
    }

def get_db_connection(with_database=True):
    """
    Create a connection to the MySQL database
    
    Args:
        with_database: If True, includes the database name in connection.
                      If False, connects to MySQL without selecting a database.
    
    Returns:
        MySQL connection object or None if connection fails
    """
    try:
        # Get database configuration 
        config = get_db_config()
        connection_params = dict(config)
        
        # Optionally remove database name from connection parameters
        if not with_database:
            connection_params.pop('database', None)
        
        print(f"Connecting to MySQL at {config['host']}:{config['port']}")
        
        connection = mysql.connector.connect(**connection_params)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            return connection
        else:
            print("Failed to connect to MySQL database")
            return None
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None 