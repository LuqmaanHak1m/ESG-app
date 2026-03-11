FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY article_processor.py .
COPY templates/ templates/
COPY static/ static/

# Create data directory for local CSV storage
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATA_SOURCE=local

# Run the application
CMD ["python", "-u", "app.py"]
