# ESG Database – Flask Integration Guide

This document explains how the Flask app should connect to the ESG pipeline database and read data from it.  
The Flask app **does not need to create or modify tables**, it only needs to **query the existing database**.

---

# 1. Database Connection

The Flask app should connect using the `DATABASE_URL` environment variable.

Example format:

    DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE

Example:

    postgresql://user:password@localhost:5432/esg_db

---

# 2. Example Python Connection (psycopg2)

Example Python code:

    import os
    import psycopg2

    DATABASE_URL = os.getenv("DATABASE_URL")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT company_name, title
    FROM articles
    LIMIT 10
    """)

    rows = cursor.fetchall()

    conn.close()

    print(rows)

---

# 3. Main Tables Used by the Flask App

The Flask app mainly needs to read from **three tables**.

---

## articles

Stores scraped ESG news articles.

Important columns:

| column | description |
|------|-------------|
| id | article ID |
| company_name | company referenced in article |
| source | website the article came from |
| title | article headline |
| introduction | article summary |
| published_at | publication date |
| url | article link |

---

## article_scores

Stores LLM ESG classifications for each article.

Important columns:

| column | description |
|------|-------------|
| article_id | references `articles.id` |
| environmental | total environmental score |
| social | total social score |
| governance | total governance score |
| climate_transition | environmental sub-score |
| labour_relations | social sub-score |
| board_management | governance sub-score |

---

## esg_scores

Stores company ESG metrics scraped from LSEG.

Important columns:

| column | description |
|------|-------------|
| company | company name |
| industry | company industry |
| category | ESG category |
| metric | ESG metric name |
| score | metric value |
| source | data provider |

---

# 4. Example Query: Articles With Scores

Example SQL query:

    SELECT
        a.company_name,
        a.title,
        a.source,
        a.published_at,
        s.environmental,
        s.social,
        s.governance
    FROM articles a
    LEFT JOIN article_scores s
        ON a.id = s.article_id
    ORDER BY a.published_at DESC;

---

# 5. Example Query: Latest Articles for a Company

    SELECT *
    FROM articles
    WHERE company_name = 'nike'
    ORDER BY published_at DESC
    LIMIT 20;

---

# 6. Example Query: ESG Metrics for a Company

    SELECT category, metric, score
    FROM esg_scores
    WHERE company = 'Nike';

---

# 7. Notes

- The Flask app should **read data from the database**, not from CSV files.
- CSV files are only used by the data pipeline during scraping and scoring.
- Articles may exist **without scores**, so queries should typically use `LEFT JOIN`.
