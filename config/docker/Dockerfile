FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads \
    && chown -R 1000:1000 /app \
    && chmod -R 755 /app \
    && chmod -R 775 /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    UPLOAD_FOLDER=/app/uploads

# Expose port
EXPOSE 5000

# Run the application - no entrypoint
CMD python -c "from app.core.database import initialize_database; initialize_database()" && \
    gunicorn --bind 0.0.0.0:5000 \
    --workers 2 \
    --threads 4 \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    --capture-output \
    wsgi:app 