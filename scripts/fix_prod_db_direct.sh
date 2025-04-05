#!/bin/bash
# Direct database fix script for production environment
set -e

echo "====== Music Mix Analyzer Database Fix ======"
echo "Running from: $(pwd)"

# Check if we're in the right directory
if [[ ! -f "scripts/fix_columns.sql" ]]; then
    echo "Error: Script must be run from the project root directory!"
    echo "Please cd to the project root and try again."
    exit 1
fi

# Get the database credentials from docker-compose.yml if not set
DB_USER=${MYSQL_USER:-mixanalytic_db}
DB_PASS=${MYSQL_PASSWORD:-"FH[@q#Z4YzQq1@8#"}
DB_NAME=${MYSQL_DATABASE:-music_analyzer}

# Show what we're using
echo "Using database: $DB_NAME"
echo "Using user: $DB_USER"

# Run the SQL script inside the container
echo "Running SQL fix script..."
docker-compose exec -T db mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < scripts/fix_columns.sql

if [ $? -eq 0 ]; then
    echo "✅ Database schema fixed successfully!"
else
    echo "❌ Failed to fix database schema"
    echo "Trying alternative approach..."
    
    # Alternative approach using docker-compose command
    echo "CREATE TABLE IF NOT EXISTS songs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255) NOT NULL DEFAULT '',
        original_name VARCHAR(255) NOT NULL DEFAULT '',
        file_hash VARCHAR(64) NOT NULL,
        file_path VARCHAR(255) NOT NULL DEFAULT '',
        is_instrumental BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        analysis_json LONGTEXT NULL,
        INDEX(file_hash)
    );" > scripts/temp_fix.sql
    
    docker-compose exec -T db mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < scripts/temp_fix.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Alternative fix successful!"
    else
        echo "❌ All attempts failed. You may need to fix the database manually."
        exit 1
    fi
fi

echo "====== Fix process completed ======" 