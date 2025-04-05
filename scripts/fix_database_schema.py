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

def check_column_types(cursor, columns):
    """
    Check if columns have the right data types
    """
    column_types = {}
    try:
        cursor.execute("DESCRIBE songs")
        table_columns = cursor.fetchall()
        for col in table_columns:
            column_types[col['Field']] = col['Type']
        return column_types
    except Error as e:
        print(f"Error checking column types: {e}")
        return {}

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
        # Check database character set
        cursor.execute("SELECT @@character_set_database, @@collation_database")
        db_charset = cursor.fetchone()
        print(f"Database character set: {db_charset}")
        
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
        
        print(f"Existing columns: {', '.join(column_names)}")
        
        # Check for legacy column names that might need migration
        has_title = 'title' in column_names
        has_analysis_data = 'analysis_data' in column_names
        
        if has_title or has_analysis_data:
            print("Found legacy column names, will perform data migration")
        
        # List of required columns and their definitions
        required_columns = {
            'id': 'INT AUTO_INCREMENT PRIMARY KEY',
            'filename': 'VARCHAR(255) NOT NULL DEFAULT ""',
            'original_name': 'VARCHAR(255) NOT NULL DEFAULT ""',
            'file_hash': 'VARCHAR(64) NOT NULL DEFAULT ""',
            'file_path': 'VARCHAR(255) NOT NULL DEFAULT ""',
            'is_instrumental': 'BOOLEAN DEFAULT FALSE',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'analysis_json': 'LONGTEXT NULL'
        }
        
        # Check which columns are missing
        missing_columns = [col for col in required_columns.keys() if col not in column_names]
        
        if not missing_columns:
            print("All required columns exist!")
        else:
            print(f"Missing columns: {', '.join(missing_columns)}")
            
            # Add missing columns
            for column in missing_columns:
                definition = required_columns[column]
                sql = f"ALTER TABLE songs ADD COLUMN {column} {definition}"
                print(f"Adding column: {sql}")
                try:
                    cursor.execute(sql)
                    print(f"Column {column} added successfully")
                except Error as e:
                    print(f"Error adding column {column}: {e}")
                    # Try alternative approach if adding column fails
                    if "Duplicate column" in str(e):
                        print(f"Column {column} already exists but wasn't detected. Skipping.")
                    else:
                        print(f"Could not add column {column}. This may affect application functionality.")
            
            connection.commit()
            print("All missing columns added successfully!")
        
        # Migrate data from legacy columns if needed
        if has_title or has_analysis_data:
            print("Migrating data from legacy columns...")
            
            # Check if migration is needed
            should_migrate_title = has_title and 'filename' in column_names and 'original_name' in column_names
            should_migrate_analysis = has_analysis_data and 'analysis_json' in column_names
            
            if should_migrate_title or should_migrate_analysis:
                try:
                    # Get all records
                    cursor.execute("SELECT * FROM songs")
                    records = cursor.fetchall()
                    migrated = 0
                    
                    for record in records:
                        updates = []
                        params = []
                        
                        # If title exists and filename is empty, migrate title to filename
                        if should_migrate_title and record.get('title') and not record.get('filename'):
                            updates.append("filename = %s")
                            params.append(record['title'])
                        
                        # If title exists and original_name is empty, migrate title to original_name
                        if should_migrate_title and record.get('title') and not record.get('original_name'):
                            updates.append("original_name = %s")
                            params.append(record['title'])
                        
                        # If analysis_data exists and analysis_json is empty, migrate analysis_data to analysis_json
                        if should_migrate_analysis and record.get('analysis_data') and not record.get('analysis_json'):
                            updates.append("analysis_json = %s")
                            params.append(record['analysis_data'])
                        
                        # If there are updates to make
                        if updates and params:
                            # Add the record ID to params
                            params.append(record['id'])
                            
                            # Update the record
                            update_sql = f"UPDATE songs SET {', '.join(updates)} WHERE id = %s"
                            cursor.execute(update_sql, params)
                            migrated += 1
                    
                    if migrated > 0:
                        connection.commit()
                        print(f"Data migration complete! {migrated} records updated.")
                    else:
                        print("No data migration needed.")
                except Error as e:
                    print(f"Error during data migration: {e}")
                    # Continue even if migration fails
        
        # Verify file_hash constraints
        try:
            cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.statistics 
            WHERE table_schema = DATABASE() 
            AND table_name = 'songs' 
            AND column_name = 'file_hash' 
            AND non_unique = 0
            """)
            has_unique = cursor.fetchone()['count'] > 0
            
            if not has_unique:
                print("Adding index to file_hash column...")
                try:
                    cursor.execute("ALTER TABLE songs ADD INDEX (file_hash)")
                    connection.commit()
                    print("INDEX added to file_hash column.")
                except Error as e:
                    print(f"Warning: Could not add index to file_hash: {e}")
        except Error as e:
            print(f"Error checking file_hash constraints: {e}")
        
        # Verify required columns again
        cursor.execute("DESCRIBE songs")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        missing_after_fix = [col for col in ['filename', 'original_name', 'analysis_json'] if col not in column_names]
        
        if missing_after_fix:
            print(f"WARNING: Still missing critical columns after fix: {', '.join(missing_after_fix)}")
            print("Database schema might not be fully compatible!")
            return False
        
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