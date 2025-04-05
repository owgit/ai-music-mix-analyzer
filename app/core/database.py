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
from app.core.db_utils import get_db_connection, get_db_config

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
        # First check if song with this hash already exists
        cursor.execute("SELECT id FROM songs WHERE file_hash = %s", (file_hash,))
        existing_song = cursor.fetchone()
        if existing_song:
            print(f"Song with hash {file_hash} already exists in database with ID: {existing_song[0]}")
            return None  # Return None to indicate no new record was created
        
        # Insert the song with standard schema
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

def delete_song(identifier):
    """
    Delete a song from the database by various identifiers
    
    Args:
        identifier: Can be file_hash, filename, or original_name
        
    Returns:
        Boolean indicating success or failure
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    try:
        # First, try as a file_hash (most reliable)
        if len(identifier) >= 32:  # If it looks like a hash
            print(f"Attempting to delete song with file_hash: {identifier}")
            cursor.execute("SELECT id, file_path FROM songs WHERE file_hash = %s", (identifier,))
            result = cursor.fetchone()
            
            if result:
                print(f"Found song with file_hash, ID: {result[0]}, file path: {result[1]}")
                cursor.execute("DELETE FROM songs WHERE file_hash = %s", (identifier,))
                connection.commit()
                deleted_rows = cursor.rowcount
                print(f"Deleted {deleted_rows} rows from songs table using file_hash")
                return deleted_rows > 0
        
        # Next, try as a filename (exact match)
        print(f"Attempting to delete song with filename: {identifier}")
        cursor.execute("SELECT id, file_path FROM songs WHERE filename = %s", (identifier,))
        result = cursor.fetchone()
        
        if result:
            print(f"Found song with filename, ID: {result[0]}, file path: {result[1]}")
            cursor.execute("DELETE FROM songs WHERE filename = %s", (identifier,))
            connection.commit()
            deleted_rows = cursor.rowcount
            print(f"Deleted {deleted_rows} rows from songs table using filename")
            return deleted_rows > 0
            
        # Try with original_name (exact match)
        print(f"Attempting to delete song with original_name: {identifier}")
        cursor.execute("SELECT id, file_path FROM songs WHERE original_name = %s", (identifier,))
        result = cursor.fetchone()
        
        if result:
            print(f"Found song with original_name, ID: {result[0]}, file path: {result[1]}")
            cursor.execute("DELETE FROM songs WHERE original_name = %s", (identifier,))
            connection.commit()
            deleted_rows = cursor.rowcount
            print(f"Deleted {deleted_rows} rows from songs table using original_name")
            return deleted_rows > 0
            
        # Try with LIKE for both filename and original_name (more permissive)
        print(f"Attempting to find song with LIKE: %{identifier}%")
        cursor.execute("SELECT id, file_path, file_hash FROM songs WHERE filename LIKE %s OR original_name LIKE %s", 
                      (f"%{identifier}%", f"%{identifier}%"))
        result = cursor.fetchone()
        
        if result:
            file_hash = result[2]
            print(f"Found song with LIKE search, ID: {result[0]}, file path: {result[1]}, hash: {file_hash}")
            cursor.execute("DELETE FROM songs WHERE id = %s", (result[0],))
            connection.commit()
            deleted_rows = cursor.rowcount
            print(f"Deleted {deleted_rows} rows from songs table using LIKE and ID")
            return deleted_rows > 0
        
        # Not found with any method
        print(f"No song found with any identifier matching: {identifier}")
        return False
    except Error as e:
        print(f"Error deleting song: {e}")
        connection.rollback()
        return False
    finally:
        # Make sure all results are consumed before closing
        if cursor.with_rows:
            cursor.fetchall()
        cursor.close()
        connection.close()

# Keep the old function name for backward compatibility
def delete_song_by_filename(filename):
    """
    Legacy function for backward compatibility
    Now delegates to the more versatile delete_song function
    """
    return delete_song(filename) 