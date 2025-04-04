#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for MySQL to be ready..."
python /app/scripts/wait_for_db.py

# Initialize the database
echo "Initializing database..."
python -c "
from app import create_app
with create_app().app_context():
    from app.core.database import initialize_database
    initialize_database()
"

# Execute the CMD
echo "Starting application..."
exec "$@" 