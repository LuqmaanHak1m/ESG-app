# Database Setup Guide

This document explains how to set up the PostgreSQL database for the ESG Dashboard application.

## Quick Start

### Option 1: Local Development (Docker Compose)

The easiest way to get started locally:

```bash
docker-compose up --build
```

This will:
1. Create a PostgreSQL container
2. Create the required tables automatically
3. Start the Flask application

The database will be empty initially. You'll need to populate it with your data.

### Option 2: Cloud Database (AWS RDS, Google Cloud SQL, etc.)

1. **Create a PostgreSQL database** on your cloud provider
2. **Run the schema** to create tables:

```bash
psql postgresql://user:password@your-host:5432/your_db < schema.sql
```

3. **Set the DATABASE_URL** environment variable:

```bash
export DATABASE_URL=postgresql://user:password@your-host:5432/your_db
```

4. **Start the application:**

```bash
docker-compose up --build
```

## Database Schema

The application requires three tables:

### 1. articles

Stores ESG news articles.

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    title TEXT NOT NULL,
    introduction TEXT,
    published_at DATE,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example data:**
```sql
INSERT INTO articles (company_name, source, title, introduction, published_at, url)
VALUES (
    'nike',
    'ESG News',
    'Nike Appoints Chief Sustainability Officer',
    'Nike has appointed a new Chief Sustainability Officer...',
    '2026-03-04',
    'https://example.com/article'
);
```

### 2. article_scores

Stores LLM-generated ESG scores for each article.

```sql
CREATE TABLE article_scores (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    environmental DECIMAL(5, 2),
    social DECIMAL(5, 2),
    governance DECIMAL(5, 2),
    climate_transition DECIMAL(5, 2),
    energy_resource DECIMAL(5, 2),
    biodiversity DECIMAL(5, 2),
    water_use DECIMAL(5, 2),
    waste_pollution DECIMAL(5, 2),
    labour_relations DECIMAL(5, 2),
    health_safety DECIMAL(5, 2),
    human_rights_community DECIMAL(5, 2),
    board_management DECIMAL(5, 2),
    shareholder_rights DECIMAL(5, 2),
    conduct_anti_corruption DECIMAL(5, 2),
    tax_transparency_accounting DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example data:**
```sql
INSERT INTO article_scores (
    article_id, environmental, social, governance,
    climate_transition, labour_relations, board_management
) VALUES (
    1, 0.0, 0.3, 0.3,
    0.0, 0.0, 0.3
);
```

### 3. esg_scores

Stores company ESG metrics from data providers (e.g., LSEG).

```sql
CREATE TABLE esg_scores (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    category VARCHAR(50) NOT NULL,
    metric VARCHAR(255) NOT NULL,
    score DECIMAL(5, 2),
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example data:**
```sql
INSERT INTO esg_scores (company, industry, category, metric, score, source)
VALUES (
    'Nike',
    'Apparel',
    'Environmental',
    'Carbon Emissions',
    3.5,
    'LSEG'
);
```

## Data Population

### From CSV Files

If you have CSV files with your data:

```bash
# Using psql COPY command
psql postgresql://user:password@host:5432/db -c "
COPY articles(company_name, source, title, introduction, published_at, url)
FROM '/path/to/articles.csv' WITH (FORMAT csv, HEADER true);
"
```

### From Your Data Pipeline

Your ESG data pipeline should:

1. Extract articles from news sources
2. Generate ESG scores using LLM analysis
3. Fetch company ESG metrics from data providers
4. Insert data into the three tables

Example Python code:

```python
import psycopg2

conn = psycopg2.connect("postgresql://user:password@host:5432/db")
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

## Verification

### Check if tables exist:

```bash
psql postgresql://user:password@host:5432/db -c "\dt"
```

### Check data in tables:

```bash
psql postgresql://user:password@host:5432/db -c "SELECT COUNT(*) FROM articles;"
psql postgresql://user:password@host:5432/db -c "SELECT COUNT(*) FROM article_scores;"
psql postgresql://user:password@host:5432/db -c "SELECT COUNT(*) FROM esg_scores;"
```

### View sample data:

```bash
psql postgresql://user:password@host:5432/db -c "SELECT * FROM articles LIMIT 5;"
```

## Troubleshooting

### Tables don't exist

Run the schema file:

```bash
psql postgresql://user:password@host:5432/db < schema.sql
```

### Connection refused

Check your DATABASE_URL:

```bash
echo $DATABASE_URL
```

Verify the host, port, username, and password are correct.

### No data showing in app

1. Verify tables have data:
```bash
psql postgresql://user:password@host:5432/db -c "SELECT COUNT(*) FROM articles;"
```

2. Check app logs:
```bash
docker-compose logs esg-app
```

## Performance Optimization

The schema includes indexes for common queries:

- `idx_articles_company` - Fast company lookups
- `idx_articles_date` - Fast date range queries
- `idx_article_scores_article_id` - Fast score lookups
- `idx_esg_scores_company` - Fast ESG metric lookups
- `idx_esg_scores_category` - Fast category filtering

For large datasets, consider:

1. **Partitioning** articles by date
2. **Materialized views** for aggregated data
3. **Read replicas** for analytics queries
4. **Connection pooling** (PgBouncer)

## Backup and Recovery

### Backup database:

```bash
pg_dump postgresql://user:password@host:5432/db > backup.sql
```

### Restore database:

```bash
psql postgresql://user:password@host:5432/db < backup.sql
```

## Next Steps

1. Create your PostgreSQL database
2. Run `schema.sql` to create tables
3. Populate tables with your data
4. Set `DATABASE_URL` environment variable
5. Start the application with `docker-compose up`
