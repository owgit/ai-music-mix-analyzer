#!/usr/bin/env python3
"""
Script to fix database schema issues in a Docker environment.
Ensures all required columns exist in the songs table.
"""

import os
import sys
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
    
    def get_db_connection(with_database=True):
        try:
            config = get_db_config()
            connection_params = dict(config)
            
            if not with_database:
                connection_params.pop('database', None)
                
            connection = mysql.connector.connect(**connection_params)
            
            if connection.is_connected():
                return connection
            else:
                print("Failed to connect to MySQL database")
                return None
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

def fix_schema():
    """
    Fix the database schema by ensuring all required columns exist
    """
    print("Starting database schema fix...")
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    cursor = connection.cursor(dictionary=True)
    try:
        # First check if the table exists
        cursor.execute("SHOW TABLES LIKE 'songs'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating songs table from scratch...")
            # Create the table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS `songs` (
              `id` INT AUTO_INCREMENT PRIMARY KEY,
              `filename` VARCHAR(255) NOT NULL,
              `original_name` VARCHAR(255) NOT NULL,
              `file_hash` VARCHAR(64) NOT NULL UNIQUE,
              `file_path` VARCHAR(255) NOT NULL,
              `is_instrumental` BOOLEAN DEFAULT FALSE,
              `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              `analysis_json` LONGTEXT NULL,
              INDEX(file_hash)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """
            cursor.execute(create_table_sql)
            connection.commit()
            print("Songs table created successfully!")
            return True
        
        # If table exists, get current columns
        print("Songs table exists, checking for missing columns...")
        cursor.execute("DESCRIBE songs")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        # List of required columns and their definitions
        required_columns = {
            'id': 'INT AUTO_INCREMENT PRIMARY KEY',
            'filename': 'VARCHAR(255) NOT NULL',
            'original_name': 'VARCHAR(255) NOT NULL',
            'file_hash': 'VARCHAR(64) NOT NULL',
            'file_path': 'VARCHAR(255) NOT NULL',
            'is_instrumental': 'BOOLEAN DEFAULT FALSE',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'analysis_json': 'LONGTEXT NULL'
        }
        
        # Check which columns are missing
        missing_columns = [col for col in required_columns.keys() if col not in column_names]
        
        if not missing_columns:
            print("All required columns exist!")
            return True
        
        print(f"Missing columns: {', '.join(missing_columns)}")
        
        # Add missing columns
        for column in missing_columns:
            definition = required_columns[column]
            sql = f"ALTER TABLE songs ADD COLUMN {column} {definition}"
            print(f"Adding column: {sql}")
            cursor.execute(sql)
        
        connection.commit()
        print("All missing columns added successfully!")
        
        # If file_hash was added, check if it has a unique constraint
        if 'file_hash' in missing_columns:
            cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.statistics 
            WHERE table_schema = DATABASE() 
            AND table_name = 'songs' 
            AND column_name = 'file_hash' 
            AND non_unique = 0
            """)
            has_unique = cursor.fetchone()['count'] > 0
            
            if not has_unique:
                print("Adding UNIQUE constraint to file_hash column...")
                try:
                    cursor.execute("ALTER TABLE songs ADD UNIQUE (file_hash)")
                    connection.commit()
                    print("UNIQUE constraint added successfully!")
                except Error as e:
                    print(f"Warning: Could not add UNIQUE constraint to file_hash: {e}")
                    print("This may be due to duplicate values in the column. Will add index instead.")
                    cursor.execute("ALTER TABLE songs ADD INDEX (file_hash)")
                    connection.commit()
                    print("INDEX added to file_hash column.")
        
        print("Schema fix completed successfully!")
        return True
    except Error as e:
        print(f"Error fixing schema: {e}")
        return False
    finally:
        if cursor and hasattr(cursor, 'with_rows') and cursor.with_rows:
            cursor.fetchall()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    if fix_schema():
        print("Database schema has been fixed successfully.")
        sys.exit(0)
    else:
        print("Failed to fix database schema.")
        sys.exit(1) 