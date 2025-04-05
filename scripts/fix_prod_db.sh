#!/bin/bash
# Script to fix database schema issues on production server
set -e

echo "====== Database Schema Fix for Production ======"
echo "Running from: $(pwd)"

# Check if we're in the right directory
if [[ ! -f "scripts/fix_database_schema.py" ]]; then
    echo "Error: Script must be run from the project root directory!"
    echo "Please cd to the project root and try again."
    exit 1
fi

# Make sure script is executable
chmod +x scripts/fix_database_schema.py

# For debugging
echo "MySQL Host: ${MYSQL_HOST:-db}"
echo "MySQL Database: ${MYSQL_DATABASE:-music_analyzer}"

# Fix the database schema
echo "Running database schema fix script..."
python scripts/fix_database_schema.py

if [ $? -eq 0 ]; then
    echo "✅ Database schema fixed successfully!"
else
    echo "❌ Failed to fix database schema"
    echo "Check logs for details"
    exit 1
fi

# For manual SQL execution if needed
echo "
If you need to manually fix the schema, use these commands:

ALTER TABLE songs ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE songs ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT NULL;

# To migrate data from legacy columns:
UPDATE songs SET filename = title WHERE title IS NOT NULL AND filename = '';
UPDATE songs SET original_name = title WHERE title IS NOT NULL AND original_name = '';
UPDATE songs SET analysis_json = analysis_data WHERE analysis_data IS NOT NULL AND analysis_json IS NULL;
"

echo "====== Fix process completed ======" 