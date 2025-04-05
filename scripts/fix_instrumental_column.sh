#!/bin/bash
# Fix for the missing is_instrumental column issue in production
set -e

echo "====== Music Mix Analyzer Column Fix ======"
echo "Running from: $(pwd)"

# Get the database credentials from environment or use defaults
DB_USER=${MYSQL_USER:-mixanalytic_db}
DB_PASS=${MYSQL_PASSWORD:-"FH[@q#Z4YzQq1@8#"}
DB_HOST=${MYSQL_HOST:-db}
DB_PORT=${MYSQL_PORT:-3306}
DB_NAME=${MYSQL_DATABASE:-music_analyzer}

# Show what we're using
echo "Using database: $DB_NAME"
echo "Using user: $DB_USER"

# Check if we're in Docker environment
if [ -f /app/scripts/fix_instrumental_column.sql ]; then
  SQL_PATH="/app/scripts/fix_instrumental_column.sql"
  echo "Running in Docker environment"
  
  # Run the SQL script
  echo "Fixing is_instrumental column..."
  mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SQL_PATH"
else
  # For running directly on the server
  if [ ! -f "scripts/fix_instrumental_column.sql" ]; then
    echo "Error: Script must be run from project root directory"
    exit 1
  fi
  
  SQL_PATH="scripts/fix_instrumental_column.sql"
  echo "Running in host environment"
  
  # Run the SQL script using docker-compose
  echo "Fixing is_instrumental column..."
  docker-compose exec -T db mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SQL_PATH"
fi

if [ $? -eq 0 ]; then
  echo "✅ Column fix applied successfully!"
else
  echo "❌ Failed to apply column fix"
  
  # Direct approach as fallback
  echo "Trying fallback approach..."
  
  if [ -f /app/scripts/fix_instrumental_column.sql ]; then
    # In Docker, use direct mysql command
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "ALTER TABLE songs ADD COLUMN IF NOT EXISTS is_instrumental BOOLEAN DEFAULT FALSE; ALTER TABLE songs ADD COLUMN IF NOT EXISTS file_path VARCHAR(255) NOT NULL DEFAULT '';"
  else
    # On host, use docker-compose exec
    docker-compose exec db mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "ALTER TABLE songs ADD COLUMN IF NOT EXISTS is_instrumental BOOLEAN DEFAULT FALSE; ALTER TABLE songs ADD COLUMN IF NOT EXISTS file_path VARCHAR(255) NOT NULL DEFAULT '';"
  fi
  
  if [ $? -eq 0 ]; then
    echo "✅ Fallback fix applied successfully!"
  else
    echo "❌ All attempts failed. Please fix manually."
    exit 1
  fi
fi

echo "====== Fix process completed ======" 