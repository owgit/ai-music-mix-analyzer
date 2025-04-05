import os
import sys
import mysql.connector
from mysql.connector import Error

# Add path to allow importing from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
                print("Creating songs table...")
                # SQL to create a new table
                create_songs_table = """
                CREATE TABLE IF NOT EXISTS `songs` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `title` varchar(255) NOT NULL,
                  `artist` varchar(255) DEFAULT NULL,
                  `album` varchar(255) DEFAULT NULL,
                  `genre` varchar(100) DEFAULT NULL,
                  `year` int DEFAULT NULL,
                  `duration` float DEFAULT NULL,
                  `file_path` varchar(255) DEFAULT NULL,
                  `file_hash` varchar(255) DEFAULT NULL,
                  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  `analysis_data` JSON DEFAULT NULL,
                  `user_id` int DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  KEY `title_artist_idx` (`title`, `artist`),
                  KEY `file_hash_idx` (`file_hash`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
                cursor.execute(create_songs_table)
                print("Songs table created successfully!")
            else:
                print("Songs table already exists")
                
                # Check if file_hash column exists and add it if missing
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'songs' 
                AND COLUMN_NAME = 'file_hash'
                """, (db_config['database'],))
                
                column_exists = cursor.fetchone()[0]
                
                if not column_exists:
                    print("Adding file_hash column...")
                    cursor.execute("""
                    ALTER TABLE `songs` 
                    ADD COLUMN `file_hash` varchar(255) DEFAULT NULL
                    """)
                    
                    # Check if index exists and add if missing
                    cursor.execute("""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.STATISTICS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'songs' 
                    AND INDEX_NAME = 'file_hash_idx'
                    """, (db_config['database'],))
                    
                    index_exists = cursor.fetchone()[0]
                    
                    if not index_exists:
                        print("Adding file_hash index...")
                        cursor.execute("""
                        ALTER TABLE `songs` 
                        ADD INDEX `file_hash_idx` (`file_hash`)
                        """)
                    
                    print("file_hash column added successfully!")
                else:
                    print("file_hash column already exists")
                
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            return True
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    initialize_database() 