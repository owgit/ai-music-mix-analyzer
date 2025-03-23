FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0 \
    && pip install --no-cache-dir setproctitle

# Create necessary directories with proper permissions
RUN mkdir -p /app/static/uploads \
    /app/static/img \
    /var/log/app \
    /var/www/.config/matplotlib \
    /dev/shm/librosa_cache \
    && chown -R www-data:www-data /app /var/log/app /var/www/.config /dev/shm/librosa_cache \
    && chmod -R 755 /app \
    && chmod -R 777 /app/static/uploads /app/static/img /var/log/app /var/www/.config/matplotlib /dev/shm/librosa_cache

# Copy application code
COPY . .

# Create a health check endpoint
RUN echo 'from flask import Blueprint\nhealthcheck_bp = Blueprint("healthcheck", __name__)\n\n@healthcheck_bp.route("/health")\ndef health_check():\n    return "OK", 200' > app/healthcheck.py

# Update __init__.py to register health check
RUN sed -i '/from app.api.routes import api_bp/a \    from app.healthcheck import healthcheck_bp\n    app.register_blueprint(healthcheck_bp)' app/__init__.py

# Set environment variables
ENV FLASK_APP=app:create_app \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/var/www/.config/matplotlib \
    LIBROSA_CACHE_DIR=/dev/shm/librosa_cache \
    NUMBA_CACHE_DIR=/dev/shm/numba_cache \
    PYTHONHASHSEED=0

# Switch to non-root user
USER www-data

# Expose port
EXPOSE 5000

# Run the application with gunicorn for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--worker-class", "gthread", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-tmp-dir", "/dev/shm", \
     "--timeout", "300", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "/var/log/app/access.log", \
     "--error-logfile", "/var/log/app/error.log", \
     "--log-level", "debug", \
     "--limit-request-line", "8190", \
     "--limit-request-field_size", "8190", \
     "wsgi:app"] 