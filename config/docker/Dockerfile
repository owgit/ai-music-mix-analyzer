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

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn explicitly
RUN pip install gunicorn==21.2.0

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create directories for uploads
RUN mkdir -p app/static/uploads app/static/img

# Expose port
EXPOSE 5000

# Run the application with gunicorn for production
# Add timeout and max-request-size for handling large files
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "--limit-request-line", "8190", "--limit-request-field_size", "8190", "wsgi:app"] 