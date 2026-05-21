# ESG Dashboard

A cloud-native Flask application for monitoring and analysing Environmental, Social and Governance (ESG) metrics across companies.
![Home page screenshot](/screenshots/home_page.png)

(For more images [go to pages](#pages-screenshots))

## Features

- **Multi-page dashboard** with home, all news, company-specific, and analytics pages
- **Real-time ESG data** from cloud PostgreSQL database
- **Risk assessment** with company-wide ESG risk status and recommended actions
- **Historical analytics** showing ESG score trends over time
- **News aggregation** with ESG impact scoring
- **Responsive design** for desktop and mobile
- **Production-ready** with gunicorn WSGI server

## Architecture

- **Frontend**: Flask + HTML/CSS/JavaScript with Chart.js
- **Backend**: Python Flask application with gunicorn
- **Database**: PostgreSQL (cloud-hosted only)
- **Deployment**: Docker containerized, cloud-native

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (AWS RDS, Google Cloud SQL, Azure Database, etc.)
- Database URL with credentials

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd esg-dashboard
```

2. **Set up database schema**
```bash
psql postgresql://user:password@host:5432/db < schema.sql
```

3. **Build and run with Docker**
```bash
DATABASE_URL=postgresql://user:password@host:5432/db docker-compose up --build
```

4. **Access the application**
Open `http://localhost:5000` in your browser

## Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)
  - Format: `postgresql://username:password@host:port/database`
- `FLASK_ENV` - Flask environment (default: production)
- `SECRET_KEY` - Flask secret key (optional, uses default in development)

## Database

The application requires three PostgreSQL tables:

- **articles** - ESG news articles
- **article_scores** - LLM-generated ESG scores for articles
- **esg_scores** - Company ESG metrics

Run `schema.sql` to create tables:
```bash
psql $DATABASE_URL < schema.sql
```

See `DATABASE_SETUP.md` for detailed schema and data population instructions.

## API Endpoints

- `GET /api/company/<company_name>` - Get company ESG data and news
- `GET /api/all-news` - Get all news articles
- `GET /api/analytics/<company_name>` - Get historical ESG data
- `GET /api/risk-assessment` - Get risk assessment for all companies
- `GET /health` - Health check endpoint

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:password@host:5432/db

# Run Flask app (development)
python app.py
```

### Docker Development

```bash
docker-compose up --build
```

## Deployment

### Cloud Platforms

The application is containerized and ready for deployment on:
- AWS ECS, Fargate, or App Runner
- Google Cloud Run
- Azure Container Instances
- Kubernetes (any distribution)
- Heroku Container Registry

See `DOCKER.md` for detailed deployment instructions.

### Production Checklist

- [ ] Use managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
- [ ] Set `SECRET_KEY` environment variable
- [ ] Enable HTTPS/SSL with reverse proxy (Nginx, CloudFront, etc.)
- [ ] Set up database backups and point-in-time recovery
- [ ] Configure monitoring and logging
- [ ] Use secrets management for credentials (AWS Secrets Manager, etc.)
- [ ] Set up auto-scaling if needed
- [ ] Configure database connection pooling for high traffic

## Data Pipeline

Your data pipeline should populate the cloud database with:

1. **Articles** - ESG news from various sources
2. **Article Scores** - LLM-generated ESG impact scores
3. **ESG Scores** - Company metrics from data providers (LSEG, etc.)

Example Python code:
```python
import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Insert article
cursor.execute("""
    INSERT INTO articles (company_name, source, title, introduction, published_at, url)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
""", ('nike', 'ESG News', 'Title', 'Summary', '2026-03-04', 'https://example.com'))

article_id = cursor.fetchone()[0]

# Insert scores
cursor.execute("""
    INSERT INTO article_scores (article_id, environmental, social, governance, ...)
    VALUES (%s, %s, %s, %s, ...)
""", (article_id, 0.0, 0.3, 0.3, ...))

conn.commit()
cursor.close()
conn.close()
```

## Pages Screenshots

### Home
![Home page screenshot](/screenshots/home_page.png)
Landing page with company overview and navigation

### All News
![All news page screenshot](/screenshots/all_news.png)
Chronological view of all ESG news articles across companies with impact metrics

### Company Pages
![Company-specific page screenshot 1](/screenshots/company_specific1.png)
![Company-specific page screenshot 1](/screenshots/company_specific2.png)
![Company-specific page screenshot 1](/screenshots/company_specific3.png)
Detailed view of individual company:
- ESG scores (Environmental, Social, Governance)
- Recent news articles with impact badges
- Adjusted scores based on article impacts

### Analytics
![Analytics page screenshot 1](/screenshots/analytics_pic1.png)
![Analytics page screenshot 2](/screenshots/analytics_pic2.png)
Historical ESG score trends with line charts showing:
- Environmental score over time
- Social score over time
- Governance score over time
- Overall ESG score

### Risk Assessment
![Risk assessment page screenshot 1](/screenshots/risk_assessment.png)
Company-wide risk dashboard showing:
- Overall ESG scores
- Risk status (Healthy, Watchlist, High Risk)
- Recommended actions (Continue Monitoring, Investigate, Escalate)
- ESG breakdown by category

## Project Structure

```
.
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── schema.sql                  # Database schema
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker Compose configuration
├── DATABASE_SETUP.md           # Database setup guide
├── DOCKER.md                   # Docker deployment guide
├── README.md                   # This file
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker ignore rules
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Home page
│   ├── all_news.html          # All news page
│   ├── company.html           # Company detail page
│   ├── analytics.html         # Analytics page
│   └── risk_assessment.html   # Risk assessment page
└── static/                     # Static files
    └── css/
        └── style.css          # Application styles
```

## Cloud-Only Architecture

This application is designed for cloud deployment:

- **No local data storage** - All data comes from cloud database
- **Stateless application** - Can be scaled horizontally
- **Environment-based configuration** - Uses environment variables only
- **Container-ready** - Docker image with gunicorn for production
- **Database-driven** - All data persisted in cloud PostgreSQL

## Troubleshooting

### Database connection failed
- Verify `DATABASE_URL` is correct
- Check firewall/security groups allow connections
- Ensure database exists and is accessible
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

### No data showing
- Verify tables exist: `psql $DATABASE_URL -c "\dt"`
- Check data in tables: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM articles;"`
- View app logs: `docker-compose logs esg-app`

### Application won't start
- Check Docker logs: `docker-compose logs esg-app`
- Verify environment variables are set: `docker-compose exec esg-app env | grep DATABASE_URL`
- Ensure database is accessible and tables exist

## License

See LICENSE file for details.

## Support

For issues or questions, please refer to:
- `DATABASE_SETUP.md` - Database configuration and schema
- `DOCKER.md` - Docker and cloud deployment
- `app.py` - Application code and API endpoints


