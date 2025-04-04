#!/bin/bash

# Get DB credentials from docker-compose.override.yml (or use defaults if not available)
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
DB_USER=${MYSQL_USER:-mixanalytic_db}
DB_PASS=${MYSQL_PASSWORD:-"FH[@q#Z4YzQq1@8#"}
DB_NAME=${MYSQL_DATABASE:-music_analyzer}

# SQL to add file_hash column
SQL_QUERY="ALTER TABLE \`songs\` 
ADD COLUMN IF NOT EXISTS \`file_hash\` varchar(255) DEFAULT NULL,
ADD INDEX IF NOT EXISTS \`file_hash_idx\` (\`file_hash\`);"

# Execute the SQL
echo "Adding file_hash column to songs table in $DB_NAME database..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$SQL_QUERY"

if [ $? -eq 0 ]; then
    echo "Column file_hash added or already exists."
else
    echo "Error adding file_hash column. Trying alternative method..."
    
    # Try alternative method without IF NOT EXISTS (for older MySQL versions)
    ALT_SQL="
    -- Check if column exists
    SET @columnExists = 0;
    SELECT COUNT(*) INTO @columnExists 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = '$DB_NAME' 
    AND TABLE_NAME = 'songs' 
    AND COLUMN_NAME = 'file_hash';

    -- Add column if it doesn't exist
    SET @sql = IF(@columnExists = 0, 
        'ALTER TABLE \`songs\` ADD COLUMN \`file_hash\` varchar(255) DEFAULT NULL', 
        'SELECT \"Column already exists\"');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;

    -- Check if index exists
    SET @indexExists = 0;
    SELECT COUNT(*) INTO @indexExists 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = '$DB_NAME' 
    AND TABLE_NAME = 'songs' 
    AND INDEX_NAME = 'file_hash_idx';

    -- Add index if it doesn't exist
    SET @sql = IF(@indexExists = 0, 
        'ALTER TABLE \`songs\` ADD INDEX \`file_hash_idx\` (\`file_hash\`)', 
        'SELECT \"Index already exists\"');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;"
    
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$ALT_SQL"
    
    if [ $? -eq 0 ]; then
        echo "Column file_hash added using alternative method."
    else
        echo "Error adding file_hash column using alternative method."
    fi
fi 