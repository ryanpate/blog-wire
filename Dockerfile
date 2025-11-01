# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p instance

# Expose port (Railway will set $PORT)
EXPOSE ${PORT:-8000}

# Run gunicorn
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
