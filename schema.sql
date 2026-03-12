-- ESG Dashboard Database Schema
-- Run this script on your PostgreSQL database to create the required tables

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    title TEXT NOT NULL,
    introduction TEXT,
    published_at DATE,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create article_scores table
CREATE TABLE IF NOT EXISTS article_scores (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
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

-- Create esg_scores table
CREATE TABLE IF NOT EXISTS esg_scores (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    category VARCHAR(50) NOT NULL,
    metric VARCHAR(255) NOT NULL,
    score DECIMAL(5, 2),
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_articles_company ON articles (company_name);

CREATE INDEX IF NOT EXISTS idx_articles_date ON articles (published_at);

CREATE INDEX IF NOT EXISTS idx_article_scores_article_id ON article_scores (article_id);

CREATE INDEX IF NOT EXISTS idx_esg_scores_company ON esg_scores (company);

CREATE INDEX IF NOT EXISTS idx_esg_scores_category ON esg_scores (category);