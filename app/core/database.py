"""
Database module for Music Mix Analyzer application
Handles MySQL connections and queries for songs
"""

import os
import mysql.connector
from mysql.connector import Error
from flask import current_app
import hashlib
import json

def get_db_connection():
    """
    Create a connection to the MySQL database
    
    Returns:
        MySQL connection object
    """
    try:
        # Get database configuration from environment variables
        host = os.environ.get('MYSQL_HOST', 'localhost')
        port = int(os.environ.get('MYSQL_PORT', 3307))  # Default to 3307 for MAMP
        user = os.environ.get('MYSQL_USER', 'root')
        password = os.environ.get('MYSQL_PASSWORD', 'root')
        database = os.environ.get('MYSQL_DATABASE', 'music_analyzer')
        
        print(f"Connecting to MySQL at {host}:{port}")
        
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
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

def create_tables_if_not_exist():
    """
    Create the necessary tables if they don't exist
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        # Create songs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            file_hash VARCHAR(64) NOT NULL UNIQUE,
            file_path VARCHAR(255) NOT NULL,
            is_instrumental BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_json LONGTEXT,
            INDEX(file_hash)
        )
        """)
        connection.commit()
        return True
    except Error as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def calculate_file_hash(file_path):
    """
    Calculate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash hexadecimal string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def find_song_by_hash(file_hash):
    """
    Find a song in the database by its hash
    
    Args:
        file_hash: SHA-256 hash of the file
        
    Returns:
        Dictionary with song data if found, None otherwise
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM songs WHERE file_hash = %s", (file_hash,))
        song = cursor.fetchone()
        return song
    except Error as e:
        print(f"Error finding song by hash: {e}")
        return None
    finally:
        # Make sure all results are consumed before closing
        if cursor.with_rows:
            cursor.fetchall()
        cursor.close()
        connection.close()

def save_song(filename, original_name, file_path, file_hash, is_instrumental, analysis_json):
    """
    Save song information to the database
    
    Args:
        filename: Unique filename in the system
        original_name: Original filename from user
        file_path: Path to the file on disk
        file_hash: SHA-256 hash of the file
        is_instrumental: Boolean indicating if the song is instrumental
        analysis_json: JSON string of analysis results
        
    Returns:
        ID of the inserted record, or None on failure
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor()
    try:
        # Try primary insertion method first
        try:
            sql = """
            INSERT INTO songs (
                filename, original_name, file_path, file_hash, is_instrumental, analysis_json
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            analysis_json_str = json.dumps(analysis_json) if analysis_json else None
            values = (filename, original_name, file_path, file_hash, is_instrumental, analysis_json_str)
            
            cursor.execute(sql, values)
            connection.commit()
            
            return cursor.lastrowid
        except Error as e:
            # If the first method fails, try alternative approach using analysis_data
            print(f"Primary insert failed: {e}, trying alternative method...")
            
            # Check if error is about missing filename column
            if "Unknown column 'filename'" in str(e):
                # Try using column names from the schema defined in init_db.py
                alt_sql = """
                INSERT INTO songs (
                    title, file_path, file_hash, analysis_data
                ) VALUES (%s, %s, %s, %s)
                """
                # Use original_name as title
                alt_values = (original_name, file_path, file_hash, json.dumps(analysis_json) if analysis_json else None)
                
                cursor.execute(alt_sql, alt_values)
                connection.commit()
                
                print("Song saved using alternative schema")
                return cursor.lastrowid
            else:
                # Re-raise if it's not the expected error
                raise
    except Error as e:
        print(f"Error saving song: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def initialize_database():
    """
    Initialize the database with necessary tables
    Should be called during application startup
    """
    return create_tables_if_not_exist()

def delete_song_by_filename(filename):
    """
    Delete a song from the database by its filename
    
    Args:
        filename: Unique filename in the system
        
    Returns:
        Boolean indicating success or failure
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        # First, try to find by filename
        print(f"Attempting to delete song with filename: {filename}")
        cursor.execute("SELECT file_path FROM songs WHERE filename = %s", (filename,))
        result = cursor.fetchone()
        
        if result:
            print(f"Found song with file path: {result[0]}")
            # Delete the song from the database
            cursor.execute("DELETE FROM songs WHERE filename = %s", (filename,))
            connection.commit()
            deleted_rows = cursor.rowcount
            print(f"Deleted {deleted_rows} rows from songs table using filename")
            return deleted_rows > 0
        else:
            print(f"No song found with filename: {filename}, trying title field...")
            # Try alternative column name (title) that might exist in database schema
            cursor.execute("SELECT file_path FROM songs WHERE title = %s", (filename,))
            result = cursor.fetchone()
            
            if result:
                print(f"Found song with title, file path: {result[0]}")
                # Delete using title field
                cursor.execute("DELETE FROM songs WHERE title = %s", (filename,))
                connection.commit()
                deleted_rows = cursor.rowcount
                print(f"Deleted {deleted_rows} rows from songs table using title")
                return deleted_rows > 0
            else:
                # Try with original_name field
                print(f"No song found with title: {filename}, trying original_name field...")
                cursor.execute("SELECT file_path FROM songs WHERE original_name LIKE %s", (f"%{filename}%",))
                result = cursor.fetchone()
                
                if result:
                    print(f"Found song with original_name, file path: {result[0]}")
                    cursor.execute("DELETE FROM songs WHERE original_name LIKE %s", (f"%{filename}%",))
                    connection.commit()
                    deleted_rows = cursor.rowcount
                    print(f"Deleted {deleted_rows} rows from songs table using original_name")
                    return deleted_rows > 0
                else:
                    print(f"No song found with any matching fields for: {filename}")
                    return False
    except Error as e:
        print(f"Error deleting song: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close() 