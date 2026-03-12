# ESG Dashboard

A cloud-native Flask application for monitoring and analyzing Environmental, Social, and Governance (ESG) metrics across companies.

## Features

- **Multi-page dashboard** with home, all news, company-specific, and analytics pages
- **Real-time ESG data** from cloud PostgreSQL database
- **Risk assessment** with company-wide ESG risk status
- **Historical analytics** showing ESG score trends over time
- **News aggregation** with ESG impact scoring
- **Responsive design** for desktop and mobile

## Architecture

- **Frontend**: Flask + HTML/CSS/JavaScript with Chart.js
- **Backend**: Python Flask application
- **Database**: PostgreSQL (cloud-hosted only)
- **Deployment**: Docker containerized

## Quick Start

### Prerequisites

- Docker installed
- PostgreSQL database (AWS RDS, Google Cloud SQL, Azure Database, etc.)
- Database URL with credentials

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd esg-dashboard
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env and add your DATABASE_URL
```

3. **Set up database schema**
```bash
psql $DATABASE_URL < schema.sql
```

4. **Build and run with Docker**
```bash
docker-compose up --build
```

5. **Access the application**
Open `http://localhost:5000` in your browser

## Configuration

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)
- `FLASK_ENV` - Flask environment (production/development)
- `SECRET_KEY` - Flask secret key (optional)

See `.env.example` for details.

## Database

The application uses three PostgreSQL tables:

- **articles** - ESG news articles
- **article_scores** - LLM-generated ESG scores for articles
- **esg_scores** - Company ESG metrics

Run `schema.sql` to create tables:
```bash
psql $DATABASE_URL < schema.sql
```

See `DATABASE_SETUP.md` for detailed schema information.

## Pages

### Home
Landing page with company overview and navigation

### All News
Chronological view of all ESG news articles across companies

### Company Pages
Detailed view of individual company:
- ESG scores (Environmental, Social, Governance)
- Recent news articles
- Impact metrics

### Analytics
Historical ESG score trends with line charts showing:
- Environmental score over time
- Social score over time
- Governance score over time
- Overall ESG score

### Risk Assessment
Company-wide risk dashboard showing:
- Overall ESG scores
- Risk status (Healthy, Watchlist, High Risk)
- Recommended actions

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

# Run Flask app
python app.py
```

### Docker Development

```bash
docker-compose up --build
```

## Deployment

### Cloud Platforms

See `DOCKER.md` for deployment instructions for:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- Kubernetes

### Production Checklist

- [ ] Use managed PostgreSQL service
- [ ] Set `SECRET_KEY` environment variable
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Use secrets management for credentials
- [ ] Set up auto-scaling if needed

## Data Pipeline

Your data pipeline should populate the cloud database with:

1. **Articles** - ESG news from various sources
2. **Article Scores** - LLM-generated ESG impact scores
3. **ESG Scores** - Company metrics from data providers

Example Python code:
```python
import psycopg2

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

## Project Structure

```
.
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── schema.sql             # Database schema
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
├── DATABASE_SETUP.md      # Database setup guide
├── DOCKER.md              # Docker deployment guide
├── .env.example           # Environment variables template
├── templates/             # HTML templates
│   ├── base.html         # Base template with navbar
│   ├── index.html        # Home page
│   ├── all_news.html     # All news page
│   ├── company.html      # Company detail page
│   ├── analytics.html    # Analytics page
│   └── risk_assessment.html # Risk assessment page
└── static/               # Static files
    └── css/
        └── style.css     # Application styles
```

## Cloud-Only Architecture

This application is designed for cloud deployment:

- **No local data storage** - All data comes from cloud database
- **Stateless application** - Can be scaled horizontally
- **Environment-based configuration** - Uses environment variables
- **Container-ready** - Docker image for easy deployment

## Troubleshooting

### Database connection failed
- Verify `DATABASE_URL` is correct
- Check firewall/security groups allow connections
- Ensure database exists and is accessible

### No data showing
- Verify tables exist: `psql $DATABASE_URL -c "\dt"`
- Check data in tables: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM articles;"`
- View app logs: `docker-compose logs esg-app`

### Application won't start
- Check Docker logs: `docker-compose logs esg-app`
- Verify environment variables are set
- Ensure database is accessible

## License

See LICENSE file for details.

## Support

For issues or questions, please refer to:
- `DATABASE_SETUP.md` - Database configuration
- `DOCKER.md` - Docker deployment
- `app.py` - Application code
