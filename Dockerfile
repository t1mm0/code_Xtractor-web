# Dockerfile for Code Block Extractor Web Application
# Purpose: Containerize Flask app for deployment on Render.com
# Last Modified: 2024-12-19
# Completeness: 100%

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static templates logs output input

# Expose port (Render.com will set PORT env var)
EXPOSE 5000

# Use gunicorn for production
# Render.com sets PORT environment variable, default to 5000 if not set
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - web_app:app
