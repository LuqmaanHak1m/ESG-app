# ESG Dashboard

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-black)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Render](https://img.shields.io/badge/Deployment-Render-46E3B7)

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://esg-dashboard-tsf1.onrender.com)

A cloud-native Flask application for monitoring and analysing Environmental, Social and Governance (ESG) metrics across companies.

🚀 Live Demo:  
https://esg-dashboard-tsf1.onrender.com

---

## Features

- Multi-page ESG dashboard
- Real-time ESG analytics
- ESG risk assessment system
- Historical ESG trend visualisation
- ESG news aggregation
- Responsive UI
- Docker containerisation
- Production-ready deployment with Render

---

## Tech Stack

- **Frontend:** Flask Templates, HTML/CSS, JavaScript, Chart.js
- **Backend:** Python Flask + Gunicorn
- **Database:** PostgreSQL
- **Deployment:** Docker + Render

---

## Screenshots

### Home
![Home page screenshot](/screenshots/home_page.png)

### Company Dashboard
![Company-specific page screenshot 1](/screenshots/company_specific1.png)

### Analytics
![Analytics page screenshot 1](/screenshots/analytics_pic1.png)

### Risk Assessment
![Risk assessment page screenshot](/screenshots/risk_assessment.png)

---

## Quick Start

### Clone Repository

```bash
git clone <repository-url>
cd esg-dashboard
```

### Configure Database

```bash
psql postgresql://user:password@host:5432/db < schema.sql
```

### Run with Docker

```bash
DATABASE_URL=postgresql://user:password@host:5432/db docker-compose up --build
```

Open:

```text
http://localhost:5000
```

---

## Environment Variables

```text
DATABASE_URL=postgresql://username:password@host:5432/database
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `/api/company/<company_name>` | Company ESG data |
| `/api/all-news` | ESG news feed |
| `/api/analytics/<company_name>` | Historical ESG analytics |
| `/api/risk-assessment` | ESG risk overview |
| `/health` | Health check |

---

## Deployment

This application is deployed on Render using Docker.

Production URL:

https://esg-dashboard-tsf1.onrender.com

---

## Project Structure

```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── schema.sql
├── templates/
├── static/
└── screenshots/
```

---

## License

See LICENSE file for details.