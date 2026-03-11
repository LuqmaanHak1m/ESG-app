# Docker Setup Guide

This application is containerized with Docker and supports both local CSV storage and future cloud storage integration.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- CSV data files (`esg_scores.csv` and `articles_scored.csv`)

### Running with Local Storage (Default)

1. **Create data directory and copy CSV files:**
```bash
mkdir -p data
cp esg_scores.csv data/
cp articles_scored.csv data/
```

2. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Open browser to `http://localhost:5000`

### Running with Docker Only

```bash
# Build the image
docker build -t esg-dashboard .

# Run the container
docker run -p 5000:5000 -v $(pwd)/data:/app/data esg-dashboard
```

## Configuration

### Local Storage (Default)
No additional configuration needed. CSV files should be in the `data/` directory.

### AWS S3 Storage (Future)

1. **Install boto3:**
```bash
pip install boto3
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Update `.env` with AWS credentials:**
```
DATA_SOURCE=aws
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket
AWS_REGION=us-east-1
```

4. **Run with environment file:**
```bash
docker-compose --env-file .env up
```

### Google Cloud Storage (Future)

1. **Install google-cloud-storage:**
```bash
pip install google-cloud-storage
```

2. **Update `.env`:**
```
DATA_SOURCE=gcp
GCP_PROJECT_ID=your-project
GCP_BUCKET_NAME=your-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
```

3. **Mount credentials file:**
```bash
docker run -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/credentials.json:/app/credentials.json \
  --env-file .env \
  esg-dashboard
```

## File Structure

```
.
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Files to exclude from Docker build
├── .env.example           # Environment variables template
├── data_handler.py        # Data storage abstraction layer
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── data/                  # Local CSV storage (mounted volume)
│   ├── esg_scores.csv
│   └── articles_scored.csv
├── templates/             # HTML templates
├── static/                # CSS and JavaScript
└── DOCKER.md             # This file
```

## Data Handler Architecture

The `data_handler.py` provides an abstraction layer for data storage:

- **LocalDataHandler**: Reads/writes CSV files from local filesystem
- **S3DataHandler**: Reads/writes from AWS S3 (requires boto3)
- **GCPDataHandler**: Reads/writes from Google Cloud Storage (requires google-cloud-storage)

To add a new storage provider:
1. Create a new class inheriting from `DataHandler`
2. Implement `load_csv()` and `save_csv()` methods
3. Update `get_data_handler()` factory function

## Health Check

The container includes a health check endpoint:
```bash
curl http://localhost:5000/health
```

## Troubleshooting

### CSV files not found
- Ensure `data/` directory exists
- Verify CSV files are in `data/` directory
- Check Docker volume mount: `docker inspect esg-dashboard`

### Permission denied errors
- Ensure `data/` directory has proper permissions
- On Linux: `chmod 755 data/`

### Cloud storage connection issues
- Verify credentials are correct
- Check environment variables: `docker exec esg-dashboard env`
- Review logs: `docker logs esg-dashboard`

## Production Deployment

For production, consider:

1. **Use environment variables** instead of `.env` file
2. **Set proper SECRET_KEY** in environment
3. **Use a production WSGI server** (Gunicorn):
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
   ```
4. **Add reverse proxy** (Nginx) for SSL/TLS
5. **Use managed cloud storage** (S3, GCS, Azure Blob)
6. **Implement proper logging** and monitoring

## Scaling

For horizontal scaling:
- Use Docker Swarm or Kubernetes
- Mount shared cloud storage for data
- Use load balancer (Nginx, HAProxy)
- Consider read-only replicas for analytics
