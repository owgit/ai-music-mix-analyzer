import os
import sys
import mysql.connector
from mysql.connector import Error

# Add path to allow importing from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.db_utils import get_db_connection, get_db_config
    from app.core.database import validate_schema
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
    
    def validate_schema():
        """
        Validates that the database schema matches the expected structure.
        Returns True if valid, False otherwise.
        """
        connection = get_db_connection()
        if not connection:
            print("Failed to connect to database for schema validation")
            return False
        
        cursor = connection.cursor(dictionary=True)
        try:
            # Check songs table exists and has required columns
            cursor.execute("DESCRIBE songs")
            columns = cursor.fetchall()
            column_names = [col['Field'] for col in columns]
            
            required_columns = ['id', 'filename', 'original_name', 'analysis_json', 'file_hash']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"Schema validation failed: missing required columns: {', '.join(missing_columns)}")
                return False
                
            print("Schema validation passed: all required columns exist")
            return True
        except Error as e:
            print(f"Error validating schema: {e}")
            return False
        finally:
            if cursor and hasattr(cursor, 'with_rows') and cursor.with_rows:
                cursor.fetchall()
            cursor.close()
            connection.close()

def initialize_database():
    """Initialize database tables if they don't exist"""
    try:
        # Get database config 
        db_config = get_db_config()
        
        # Create connection
        connection = get_db_connection()
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if songs table exists
            cursor.execute("SHOW TABLES LIKE 'songs'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("Creating songs table with standardized schema...")
                # SQL to create songs table with the standardized schema
                create_songs_table = """
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
                cursor.execute(create_songs_table)
                print("Songs table created successfully!")
            else:
                print("Songs table already exists")
                
                # Check for and add missing columns to ensure schema consistency
                
                # Check if filename column exists
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'songs' 
                AND COLUMN_NAME = 'filename'
                """, (db_config['database'],))
                
                has_filename = cursor.fetchone()[0] > 0
                
                # Check if original_name column exists
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'songs' 
                AND COLUMN_NAME = 'original_name'
                """, (db_config['database'],))
                
                has_original_name = cursor.fetchone()[0] > 0
                
                # Check if analysis_json column exists
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'songs' 
                AND COLUMN_NAME = 'analysis_json'
                """, (db_config['database'],))
                
                has_analysis_json = cursor.fetchone()[0] > 0
                
                # Check if file_hash column exists
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'songs' 
                AND COLUMN_NAME = 'file_hash'
                """, (db_config['database'],))
                
                has_file_hash = cursor.fetchone()[0] > 0
                
                # Add missing columns if necessary
                alterations = []
                
                if not has_filename:
                    alterations.append("ADD COLUMN `filename` VARCHAR(255) NOT NULL DEFAULT ''")
                
                if not has_original_name:
                    alterations.append("ADD COLUMN `original_name` VARCHAR(255) NOT NULL DEFAULT ''")
                
                if not has_analysis_json:
                    alterations.append("ADD COLUMN `analysis_json` LONGTEXT NULL")
                
                if not has_file_hash:
                    alterations.append("ADD COLUMN `file_hash` VARCHAR(64) NULL")
                
                if alterations:
                    print("Adding missing columns to ensure schema consistency...")
                    alter_sql = f"ALTER TABLE `songs` {', '.join(alterations)}"
                    print(f"Executing: {alter_sql}")
                    cursor.execute(alter_sql)
                    print("Columns added successfully!")
                
                # Check if file_hash index exists
                if has_file_hash:
                    cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.STATISTICS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'songs' 
                    AND INDEX_NAME = 'file_hash_idx'
                    """, (db_config['database'],))
                    
                    index_exists = cursor.fetchone()[0] > 0
                    
                    if not index_exists:
                        print("Adding file_hash index...")
                        cursor.execute("""
                        ALTER TABLE `songs` 
                        ADD INDEX `file_hash_idx` (`file_hash`)
                        """)
                        print("file_hash index added successfully!")
                
            # Migrate data from old schema to new schema if needed (title → filename, analysis_data → analysis_json)
            cursor.execute("SHOW COLUMNS FROM `songs` LIKE 'title'")
            has_title = cursor.fetchone() is not None
            
            cursor.execute("SHOW COLUMNS FROM `songs` LIKE 'analysis_data'")
            has_analysis_data = cursor.fetchone() is not None
            
            # If old schema columns exist, migrate data
            if has_title or has_analysis_data:
                print("Migrating data from legacy schema...")
                
                # Get all records that might need migration
                cursor.execute("SELECT * FROM songs")
                records = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                
                # Create dictionaries for cleaner access
                record_dicts = []
                for record in records:
                    record_dict = {}
                    for i, field in enumerate(field_names):
                        record_dict[field] = record[i]
                    record_dicts.append(record_dict)
                
                # Migrate each record if needed
                for record in record_dicts:
                    updates = []
                    params = []
                    
                    # Migrate title to filename if needed
                    if has_title and 'title' in record and record['title'] and (not has_filename or not record.get('filename')):
                        updates.append("filename = %s")
                        params.append(record['title'])
                    
                    # Migrate title to original_name if needed
                    if has_title and 'title' in record and record['title'] and (not has_original_name or not record.get('original_name')):
                        updates.append("original_name = %s")
                        params.append(record['title'])
                    
                    # Migrate analysis_data to analysis_json if needed
                    if has_analysis_data and 'analysis_data' in record and record['analysis_data'] and (not has_analysis_json or not record.get('analysis_json')):
                        updates.append("analysis_json = %s")
                        params.append(record['analysis_data'])
                    
                    # Update record if there are changes
                    if updates and params:
                        params.append(record['id'])
                        update_sql = f"UPDATE songs SET {', '.join(updates)} WHERE id = %s"
                        cursor.execute(update_sql, params)
                
                connection.commit()
                print("Data migration completed!")
            
            # Validate the schema to ensure all required columns exist
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
            # Verify schema consistency
            schema_valid = validate_schema()
            if schema_valid:
                print("Schema validation passed - database is ready to use")
                return True
            else:
                print("Schema validation failed - database may not work correctly")
                return False
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    initialize_database() 