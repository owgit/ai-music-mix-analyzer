#!/usr/bin/env python3
"""
Fix database schema for Music Mix Analyzer
This script adds missing columns required for the application to work
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.environ.get('MYSQL_HOST', 'db'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', os.environ.get('DB_ROOT_PASSWORD', 'root')),
        'database': os.environ.get('MYSQL_DATABASE', 'music_analyzer')
    }

def fix_database_schema():
    """Add missing columns to the songs table"""
    try:
        config = get_db_config()
        print(f"Connecting to MySQL at {config['host']}:{config['port']}")
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor(dictionary=True)
            
            # Get current columns
            cursor.execute("SHOW TABLES LIKE 'songs'")
            if not cursor.fetchone():
                print("Songs table does not exist. Creating it...")
                create_songs_table = """
                CREATE TABLE IF NOT EXISTS `songs` (
                  `id` INT AUTO_INCREMENT PRIMARY KEY,
                  `filename` VARCHAR(255) NOT NULL,
                  `original_name` VARCHAR(255) NOT NULL,
                  `file_hash` VARCHAR(64) NOT NULL UNIQUE,
                  `file_path` VARCHAR(255) NOT NULL DEFAULT '',
                  `is_instrumental` BOOLEAN DEFAULT FALSE,
                  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  `analysis_json` LONGTEXT NULL,
                  INDEX(file_hash)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
                cursor.execute(create_songs_table)
                print("Songs table created successfully!")
                connection.commit()
            
            # Check for existing columns
            cursor.execute("DESCRIBE songs")
            columns = cursor.fetchall()
            column_names = [col['Field'] for col in columns]
            print(f"Current columns: {column_names}")
            
            # Check and add missing columns
            required_columns = {
                'filename': "ALTER TABLE songs ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT 'unknown_filename'",
                'original_name': "ALTER TABLE songs ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT 'unknown_original_name'",
                'analysis_json': "ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT NULL",
                'file_hash': "ALTER TABLE songs ADD COLUMN file_hash VARCHAR(64) NULL, ADD INDEX(file_hash)"
            }
            
            for col_name, sql in required_columns.items():
                if col_name not in column_names:
                    print(f"Adding missing column: {col_name}")
                    cursor.execute(sql)
                    connection.commit()
                else:
                    print(f"Column {col_name} already exists")
            
            # Verify schema after changes
            cursor.execute("DESCRIBE songs")
            updated_columns = cursor.fetchall()
            updated_column_names = [col['Field'] for col in updated_columns]
            print(f"Updated columns: {updated_column_names}")
            
            # Check if all required columns are present now
            required_columns_set = set(required_columns.keys())
            updated_columns_set = set(updated_column_names)
            missing = required_columns_set - updated_columns_set
            
            if missing:
                print(f"WARNING: Still missing columns: {missing}")
                return False
            else:
                print("SUCCESS: All required columns are now present!")
                return True
                
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    success = fix_database_schema()
    sys.exit(0 if success else 1) 