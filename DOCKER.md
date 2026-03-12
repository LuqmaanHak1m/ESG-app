# Docker Setup Guide - Cloud-Only

This application is containerized with Docker and connects exclusively to cloud PostgreSQL databases. No local data storage is used.

## Prerequisites

- Docker installed
- PostgreSQL database (AWS RDS, Google Cloud SQL, Azure Database, etc.)
- Database URL with connection credentials

## Quick Start

### 1. Set up your cloud database

Create a PostgreSQL database on your cloud provider and run the schema:

```bash
psql postgresql://user:password@your-host:5432/your_db < schema.sql
```

### 2. Set DATABASE_URL environment variable

```bash
export DATABASE_URL=postgresql://user:password@your-host:5432/your_db
```

### 3. Build and run with Docker

```bash
docker-compose up --build
```

The application will start and connect to your cloud database.

### 4. Access the application

Open browser to `http://localhost:5000`

## Database Configuration

The application requires the `DATABASE_URL` environment variable pointing to your PostgreSQL database.

**Format:**
```
postgresql://username:password@host:port/database
```

**Examples:**

AWS RDS:
```
postgresql://admin:password@my-db.xxxxx.us-east-1.rds.amazonaws.com:5432/esg_db
```

Google Cloud SQL:
```
postgresql://postgres:password@35.x.x.x:5432/esg_db
```

Azure Database for PostgreSQL:
```
postgresql://user@servername:password@servername.postgres.database.azure.com:5432/esg_db
```

## Running with Docker

### Local development

```bash
docker-compose up --build
```

### Production deployment

```bash
DATABASE_URL=postgresql://user:password@host:5432/db docker-compose up -d
```

### With custom environment file

Create `.env` file:
```
DATABASE_URL=postgresql://user:password@host:5432/db
FLASK_ENV=production
```

Then run:
```bash
docker-compose up --build
```

## Database Schema

The application requires three tables. Run `schema.sql` on your cloud database:

```bash
psql $DATABASE_URL < schema.sql
```

**Tables:**
- `articles` - ESG news articles
- `article_scores` - LLM-generated ESG scores
- `esg_scores` - Company ESG metrics

See `DATABASE_SETUP.md` for detailed schema information.

## Data Population

Your data pipeline should populate the cloud database with:

1. Articles from news sources
2. ESG scores from LLM analysis
3. Company metrics from data providers

The Flask app reads directly from the cloud database.

## Health Check

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Connection refused

1. Verify DATABASE_URL is correct:
```bash
echo $DATABASE_URL
```

2. Test connection manually:
```bash
psql $DATABASE_URL -c "SELECT 1"
```

3. Check firewall/security groups allow connections

### No data showing

1. Verify tables exist:
```bash
psql $DATABASE_URL -c "\dt"
```

2. Check data in tables:
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM articles;"
```

3. View app logs:
```bash
docker-compose logs esg-app
```

## Production Deployment

### Cloud Platforms

**AWS ECS:**
```bash
docker build -t esg-dashboard .
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag esg-dashboard:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/esg-dashboard:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/esg-dashboard:latest
```

**Google Cloud Run:**
```bash
docker build -t gcr.io/$PROJECT_ID/esg-dashboard .
docker push gcr.io/$PROJECT_ID/esg-dashboard
gcloud run deploy esg-dashboard \
  --image gcr.io/$PROJECT_ID/esg-dashboard \
  --set-env-vars DATABASE_URL=$DATABASE_URL \
  --platform managed
```

**Azure Container Instances:**
```bash
docker build -t esg-dashboard .
az acr build --registry $REGISTRY_NAME --image esg-dashboard:latest .
az container create \
  --resource-group $RESOURCE_GROUP \
  --name esg-dashboard \
  --image $REGISTRY_NAME.azurecr.io/esg-dashboard:latest \
  --environment-variables DATABASE_URL=$DATABASE_URL
```

### Best Practices

1. **Use managed PostgreSQL** - AWS RDS, Google Cloud SQL, Azure Database
2. **Set SECRET_KEY** in environment
3. **Use production WSGI server** - Gunicorn is included
4. **Add reverse proxy** - Nginx for SSL/TLS
5. **Enable database backups** - Automated daily backups
6. **Monitor logs** - CloudWatch, Stackdriver, or Azure Monitor
7. **Use secrets management** - AWS Secrets Manager, Google Secret Manager, etc.

## File Structure

```
.
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Files to exclude from Docker build
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
├── DATABASE_SETUP.md     # Database setup guide
├── DOCKER.md             # This file
├── templates/            # HTML templates
└── static/               # CSS and JavaScript
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)
- `FLASK_ENV` - Flask environment (production/development)
- `SECRET_KEY` - Flask secret key (optional, uses default in development)

## Notes

- No local data storage
- All data comes from cloud database
- No CSV files or local files
- Stateless application - can be scaled horizontally
- Database connection pooling recommended for production
