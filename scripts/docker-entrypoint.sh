#!/bin/bash
set -e

echo "================ Music Mix Analyzer Startup ================"

# Wait for the database to be ready
echo "Waiting for MySQL to be ready..."
python /app/scripts/wait_for_db.py

# Copy fix_columns.sql to a writable location if it doesn't exist
if [[ ! -f "/app/scripts/fix_columns.sql" ]]; then
    echo "Creating database fix script..."
    cat > /app/scripts/fix_columns.sql << 'EOL'
-- Fix columns script for Music Mix Analyzer
-- Adds missing required columns to the songs table

-- Add filename column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'filename';

SET @add_filename = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "filename column already exists"');
PREPARE stmt FROM @add_filename;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add original_name column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'original_name';

SET @add_original_name = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "original_name column already exists"');
PREPARE stmt FROM @add_original_name;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add analysis_json column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'analysis_json';

SET @add_analysis_json = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT NULL', 
    'SELECT "analysis_json column already exists"');
PREPARE stmt FROM @add_analysis_json;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add is_instrumental column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'is_instrumental';

SET @add_is_instrumental = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN is_instrumental BOOLEAN DEFAULT FALSE', 
    'SELECT "is_instrumental column already exists"');
PREPARE stmt FROM @add_is_instrumental;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add file_path column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'file_path';

SET @add_file_path = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN file_path VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "file_path column already exists"');
PREPARE stmt FROM @add_file_path;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and fix title column
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'title';

-- If title exists, update it to have default value
SET @modify_title = IF(@col_exists > 0, 
    'ALTER TABLE songs MODIFY COLUMN title VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "title column does not exist - no modification needed"');

PREPARE stmt FROM @modify_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- If title doesn't exist, create it with a default value
SET @add_title = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "title column already exists"');

PREPARE stmt FROM @add_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Migrate data between columns if needed
UPDATE songs SET title = original_name WHERE title = '' AND original_name != '';
UPDATE songs SET title = filename WHERE title = '' AND filename != '' AND original_name = '';
UPDATE songs SET filename = title WHERE filename = '' AND title != '';
UPDATE songs SET original_name = title WHERE original_name = '' AND title != '';

-- Migrate data from title column if needed
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'title';

SET @migrate_title = IF(@col_exists > 0, 
    'UPDATE songs SET filename = title WHERE title IS NOT NULL AND (filename IS NULL OR filename = "")', 
    'SELECT "No title column to migrate from"');
PREPARE stmt FROM @migrate_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @migrate_title2 = IF(@col_exists > 0, 
    'UPDATE songs SET original_name = title WHERE title IS NOT NULL AND (original_name IS NULL OR original_name = "")', 
    'SELECT "No title column to migrate from"');
PREPARE stmt FROM @migrate_title2;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Migrate data from analysis_data column if needed
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'analysis_data';

SET @migrate_analysis = IF(@col_exists > 0, 
    'UPDATE songs SET analysis_json = analysis_data WHERE analysis_data IS NOT NULL AND analysis_json IS NULL', 
    'SELECT "No analysis_data column to migrate from"');
PREPARE stmt FROM @migrate_analysis;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Done
SELECT 'Schema fix completed successfully!' as message;
EOL
fi

# Fix database schema issues automatically
echo "Fixing database schema if needed..."
DB_USER=${MYSQL_USER:-mixanalytic_db}
DB_PASS=${MYSQL_PASSWORD:-"FH[@q#Z4YzQq1@8#"}
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
DB_NAME=${MYSQL_DATABASE:-music_analyzer}

# Try to run the fix script
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < /app/scripts/fix_columns.sql
if [ $? -ne 0 ]; then
    echo "Warning: Could not fix schema automatically, but will continue startup"
else
    echo "Schema verification and fixes applied successfully"
fi

# Initialize the database
echo "Initializing database..."
python -c "
from app import create_app
with create_app().app_context():
    from app.core.database import initialize_database
    initialize_database()
"

# Create table if it doesn't exist as a final fallback
echo "Ensuring songs table exists (fallback)..."
cat > /tmp/create_table.sql << 'EOL'
CREATE TABLE IF NOT EXISTS songs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL DEFAULT '',
    original_name VARCHAR(255) NOT NULL DEFAULT '',
    title VARCHAR(255) NOT NULL DEFAULT '',
    file_hash VARCHAR(64) NOT NULL,
    file_path VARCHAR(255) NOT NULL DEFAULT '',
    is_instrumental BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_json LONGTEXT NULL,
    INDEX(file_hash)
);
EOL

mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < /tmp/create_table.sql || true

# Execute the CMD
echo "Starting application..."
echo "================ Startup Complete ================"
exec "$@" 