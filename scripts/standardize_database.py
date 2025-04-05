#!/usr/bin/env python3
"""
One-time script to standardize the database schema.
Migrates any data from the alternative schema to the standard schema.
"""

import os
import sys
import json
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

def check_table_columns():
    """
    Check which columns exist in the songs table
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("DESCRIBE songs")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        print(f"Existing columns: {', '.join(column_names)}")
        return column_names
    except Error as e:
        print(f"Error checking table columns: {e}")
        return None
    finally:
        if cursor.with_rows:
            cursor.fetchall()
        cursor.close()
        connection.close()

def migrate_data():
    """
    Migrate data from old schema to new schema
    """
    columns = check_table_columns()
    if not columns:
        print("Failed to get column information")
        return False
    
    # Check if we need to migrate data
    has_title = 'title' in columns
    has_analysis_data = 'analysis_data' in columns
    has_filename = 'filename' in columns
    has_original_name = 'original_name' in columns
    has_analysis_json = 'analysis_json' in columns
    
    if not (has_title or has_analysis_data) or (has_filename and has_original_name and has_analysis_json):
        print("No migration needed - either using standard schema or missing key alternative fields")
        return True
    
    # Prepare the migration
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # First, get all records
        cursor.execute("SELECT * FROM songs")
        records = cursor.fetchall()
        total_records = len(records)
        print(f"Found {total_records} records to check for migration")

        # Alter table if needed
        alterations = []
        
        # Add required columns if they don't exist
        if not has_filename:
            alterations.append("ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT ''")
        
        if not has_original_name:
            alterations.append("ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT ''")
        
        if not has_analysis_json:
            alterations.append("ADD COLUMN analysis_json LONGTEXT NULL")
        
        if alterations:
            alter_sql = f"ALTER TABLE songs {', '.join(alterations)}"
            print(f"Altering table: {alter_sql}")
            cursor.execute(alter_sql)
            connection.commit()
        
        # Migrate data record by record
        migrated = 0
        for record in records:
            updates = []
            params = []
            
            # If title exists but filename is empty/default, migrate title to filename
            if has_title and record.get('title') and (not has_filename or not record.get('filename')):
                updates.append("filename = %s")
                params.append(record['title'])
            
            # If title exists but original_name is empty/default, migrate title to original_name
            if has_title and record.get('title') and (not has_original_name or not record.get('original_name')):
                updates.append("original_name = %s")
                params.append(record['title'])
            
            # If analysis_data exists but analysis_json is empty, migrate analysis_data to analysis_json
            if has_analysis_data and record.get('analysis_data') and (not has_analysis_json or not record.get('analysis_json')):
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
                
                # Commit every 100 records
                if migrated % 100 == 0:
                    connection.commit()
                    print(f"Migrated {migrated} records so far...")
        
        # Final commit
        connection.commit()
        print(f"Migration complete! {migrated} records updated.")
        
        return True
    except Error as e:
        print(f"Error during migration: {e}")
        connection.rollback()
        return False
    finally:
        if cursor.with_rows:
            cursor.fetchall()
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("Starting database schema standardization...")
    if migrate_data():
        print("Schema standardization completed successfully.")
    else:
        print("Schema standardization failed.")
        sys.exit(1) 