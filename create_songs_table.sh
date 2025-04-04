#!/bin/bash

# Get DB credentials from docker-compose.override.yml (or use defaults if not available)
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
DB_USER=${MYSQL_USER:-mixanalytic_db}
DB_PASS=${MYSQL_PASSWORD:-"FH[@q#Z4YzQq1@8#"}
DB_NAME=${MYSQL_DATABASE:-music_analyzer}

# SQL to create songs table
SQL_QUERY="CREATE TABLE IF NOT EXISTS \`songs\` (
  \`id\` int NOT NULL AUTO_INCREMENT,
  \`title\` varchar(255) NOT NULL,
  \`artist\` varchar(255) DEFAULT NULL,
  \`album\` varchar(255) DEFAULT NULL,
  \`genre\` varchar(100) DEFAULT NULL,
  \`year\` int DEFAULT NULL,
  \`duration\` float DEFAULT NULL,
  \`file_path\` varchar(255) DEFAULT NULL,
  \`created_at\` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  \`updated_at\` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  \`analysis_data\` JSON DEFAULT NULL,
  \`user_id\` int DEFAULT NULL,
  PRIMARY KEY (\`id\`),
  KEY \`title_artist_idx\` (\`title\`, \`artist\`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"

# Execute the SQL
echo "Creating songs table in $DB_NAME database if it doesn't exist..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$SQL_QUERY"

if [ $? -eq 0 ]; then
    echo "Table songs created or already exists."
else
    echo "Error creating table songs."
fi 