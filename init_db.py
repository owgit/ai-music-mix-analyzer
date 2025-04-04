import os
import mysql.connector
from mysql.connector import Error

def initialize_database():
    """Initialize database tables if they don't exist"""
    try:
        # Get database connection parameters from environment variables
        db_config = {
            'host': os.environ.get('MYSQL_HOST', 'db'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'mixanalytic_db'),
            'password': os.environ.get('MYSQL_PASSWORD', ''),
            'database': os.environ.get('MYSQL_DATABASE', 'music_analyzer')
        }
        
        # Create connection
        connection = mysql.connector.connect(**db_config)
        
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
                  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  `analysis_data` JSON DEFAULT NULL,
                  `user_id` int DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  KEY `title_artist_idx` (`title`, `artist`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
                cursor.execute(create_songs_table)
                print("Songs table created successfully!")
            else:
                print("Songs table already exists")
                
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

if __name__ == "__main__":
    initialize_database() 