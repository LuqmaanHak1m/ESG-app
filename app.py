import os
from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import datetime as dt

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')

def load_esg_data():
    """Load ESG scores from CSV"""
    try:
        df = pd.read_csv('esg_scores.csv')
        return df
    except Exception as e:
        print(f"Error loading ESG data: {e}")
        return pd.DataFrame()

def calculate_category_scores(df, company):
    """Calculate average scores by category for a company"""
    company_data = df[df['company'] == company]
    
    categories = {}
    for category in ['Environmental', 'Social', 'Governance']:
        cat_data = company_data[company_data['category'] == category]
        if not cat_data.empty:
            categories[category] = {
                'score': round(cat_data['score'].mean(), 2),
                'metrics': cat_data[['metric', 'score']].to_dict('records')
            }
    
    return categories

def process_article_data(articles_data):
    """
    Process article data from LLM analysis into dashboard format
    
    Args:
        articles_data: List of dicts or single dict with article analysis
        
    Returns:
        List of processed articles for dashboard display
    """
    if not isinstance(articles_data, list):
        articles_data = [articles_data]
    
    # Mapping from LLM field names to display names
    field_mapping = {
        'climate_transition': 'Climate Transition',
        'energy_resource': 'Energy & Resource Use', 
        'biodiversity': 'Biodiversity',
        'water_use': 'Water Use',
        'waste_pollution': 'Waste & Pollution',
        'labour_relations': 'Labour Relations',
        'health_safety': 'Health & Safety',
        'human_rights_community': 'Human Rights & Community',
        'board_management': 'Board & Management',
        'shareholder_rights': 'Shareholder Rights',
        'conduct_anti_corruption': 'Conduct & Anti-Corruption',
        'tax_transparency_accounting': 'Tax Transparency & Accounting'
    }
    
    processed_articles = []
    
    for article in articles_data:
        # Extract impact scores (exclude company and title)
        impact = {}
        for field, display_name in field_mapping.items():
            if field in article and article[field] != 0:
                impact[display_name] = article[field]
        
        # Determine overall sentiment
        impact_values = list(impact.values())
        if impact_values:
            avg_impact = sum(impact_values) / len(impact_values)
            overall_sentiment = 'positive' if avg_impact > 0 else 'negative' if avg_impact < 0 else 'neutral'
        else:
            overall_sentiment = 'neutral'
        
        processed_article = {
            'title': article.get('title', 'Unknown Article'),
            'company': article.get('company', 'Unknown Company'),
            'summary': article.get('summary', 'Analysis based on ESG impact scoring'),
            'date': article.get('date', dt.datetime.today().strftime("%d/%m/%Y")),  # Default to current date
            'impact': impact,
            'overall_sentiment': overall_sentiment
        }
        
        processed_articles.append(processed_article)
    
    return processed_articles

def calculate_adjusted_scores(original_categories, processed_articles, company):
    """
    Calculate adjusted ESG scores based on article impacts
    
    Args:
        original_categories: Original ESG category scores
        processed_articles: List of processed articles
        company: Company name to filter articles
        
    Returns:
        Dict with adjusted scores by category
    """
    # Filter articles for this company
    company_articles = [a for a in processed_articles if a['company'].lower() == company.lower()]
    
    # Calculate total impact by metric
    metric_impacts = {}
    for article in company_articles:
        for metric, impact in article['impact'].items():
            if metric not in metric_impacts:
                metric_impacts[metric] = 0
            metric_impacts[metric] += impact
    
    # Apply impacts to original scores and calculate category averages
    adjusted_categories = {}
    
    for category, category_data in original_categories.items():
        adjusted_metrics = []
        total_adjustment = 0
        
        for metric in category_data['metrics']:
            metric_name = metric['metric']
            original_score = metric['score']
            
            # Find matching impact (handle slight name variations)
            impact = 0
            for impact_metric, impact_value in metric_impacts.items():
                if (impact_metric.lower().replace(' & ', ' ').replace(' ', '') == 
                    metric_name.lower().replace(' & ', ' ').replace(' ', '')):
                    impact = impact_value
                    break
            
            adjusted_score = max(0, min(5, original_score + impact))
            metric['adjusted_score'] = round(adjusted_score, 2)
            adjusted_metrics.append(metric)
            total_adjustment += impact
        
        # Calculate new category average
        adjusted_avg = sum(m['adjusted_score'] for m in adjusted_metrics) / len(adjusted_metrics)
        
        adjusted_categories[category] = {
            'score': round(adjusted_avg, 2),
            'change': round(total_adjustment / len(adjusted_metrics), 2)
        }
    
    return adjusted_categories

@app.route('/')
def index():
    """Home page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []
    return render_template('index.html', companies=companies)

@app.route('/all-news')
def all_news():
    """All news page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []
    return render_template('all_news.html', companies=companies)

@app.route('/company/<company_name>')
def company_page(company_name):
    """Individual company page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []
    if company_name not in companies:
        return "Company not found", 404
    return render_template('company.html', company=company_name, companies=companies)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []
    selected_company = request.args.get('company', '')
    return render_template('analytics.html', companies=companies, selected_company=selected_company)

@app.route('/analytics/<company_name>')
def analytics_for_company(company_name):
    """Analytics page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []

    get_analytics(company_name)

    return render_template('analytics.html', companies=companies)

@app.route('/api/company/<company_name>')
def get_company_data(company_name):
    """API endpoint to get company ESG data"""
    df = load_esg_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    if company_name not in df['company'].values:
        return jsonify({'error': 'Company not found'}), 404
    
    categories = calculate_category_scores(df, company_name)
    
    # Example article data (this would come from your LLM analysis)
    example_articles = []
    
    if company_name == 'Nike':
        example_articles = [
            {
                "company": "Nike",
                "title": "Mitsui Signs Solar VPPA With NIKE Japan to Deliver 100% Renewable Power Across Operations",
                "climate_transition": 1.0,
                "energy_resource": 1.2,
                "summary": "Mitsui & Co. Project Solutions have signed a long term virtual power purchase agreement with NIKE Japan Group to supply renewable energy attributes generated from domestic solar power projects.",
                "date": "2024/03-08"
            },
            {
                "company": "Nike",
                "title": "Nike Announces New Sustainable Materials Initiative",
                "climate_transition": 0.8,
                "waste_pollution": 0.6,
                "biodiversity": 0.3,
                "summary": "Nike unveils plan to use 50% recycled materials in all products by 2025, reducing environmental footprint.",
                "date": "2024-03-05"
            }
        ]
    
    elif company_name == 'Adidas':
        example_articles = [
            {
                "company": "Adidas",
                "title": "Adidas Factory Workers Report Safety Concerns in Vietnam Facility",
                "health_safety": -0.7,
                "labour_relations": -0.4,
                "human_rights_community": -0.3,
                "summary": "Workers at an Adidas supplier factory in Vietnam have raised concerns about workplace safety conditions, prompting an internal investigation.",
                "date": "2024-03-05"
            },
            {
                "company": "Adidas",
                "title": "Adidas Improves Board Diversity with New Appointments",
                "board_management": 0.5,
                "conduct_anti_corruption": 0.2,
                "summary": "Adidas announces three new board members focused on sustainability and diversity initiatives.",
                "date": "2024-03-01"
            }
        ]
    
    # Process articles and calculate adjusted scores
    processed_articles = process_article_data(example_articles)
    adjusted_scores = calculate_adjusted_scores(categories, processed_articles, company_name)
    
    return jsonify({
        'company': company_name,
        'original_scores': categories,
        'adjusted_scores': adjusted_scores,
        'news_articles': processed_articles
    })

@app.route('/api/process-articles', methods=['POST'])
def process_articles():
    """
    API endpoint to process new article data
    
    Expected JSON format:
    {
        "articles": [
            {
                "company": "Nike",
                "title": "Article Title",
                "climate_transition": 1.0,
                "energy_resource": 0.5,
                ...
            }
        ]
    }
    """
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        
        if not articles:
            return jsonify({'error': 'No articles provided'}), 400
        
        processed_articles = process_article_data(articles)
        
        return jsonify({
            'processed_articles': processed_articles,
            'count': len(processed_articles)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all-news')
def get_all_news():
    """API endpoint to get all news from all companies sorted chronologically"""
    df = load_esg_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    companies = df['company'].unique().tolist()
    all_articles = []
    
    # Collect articles from all companies
    for company in companies:
        if company == 'Nike':
            articles = [
                {
                    "company": "Nike",
                    "title": "Mitsui Signs Solar VPPA With NIKE Japan to Deliver 100% Renewable Power Across Operations",
                    "climate_transition": 1.0,
                    "energy_resource": 1.2,
                    "summary": "Mitsui & Co. Project Solutions have signed a long term virtual power purchase agreement with NIKE Japan Group to supply renewable energy attributes generated from domestic solar power projects.",
                    "date": "2024-03-08"
                },
                {
                    "company": "Nike",
                    "title": "Nike Announces New Sustainable Materials Initiative",
                    "climate_transition": 0.8,
                    "waste_pollution": 0.6,
                    "biodiversity": 0.3,
                    "summary": "Nike unveils plan to use 50% recycled materials in all products by 2025, reducing environmental footprint.",
                    "date": "2024-03-05"
                }
            ]
        elif company == 'Adidas':
            articles = [
                {
                    "company": "Adidas",
                    "title": "Adidas Factory Workers Report Safety Concerns in Vietnam Facility",
                    "health_safety": -0.7,
                    "labour_relations": -0.4,
                    "human_rights_community": -0.3,
                    "summary": "Workers at an Adidas supplier factory in Vietnam have raised concerns about workplace safety conditions, prompting an internal investigation.",
                    "date": "2024-03-05"
                },
                {
                    "company": "Adidas",
                    "title": "Adidas Improves Board Diversity with New Appointments",
                    "board_management": 0.5,
                    "conduct_anti_corruption": 0.2,
                    "summary": "Adidas announces three new board members focused on sustainability and diversity initiatives.",
                    "date": "2024-03-01"
                }
            ]
        else:
            articles = []
        
        all_articles.extend(articles)
    
    # Process articles
    processed_articles = process_article_data(all_articles)
    
    # Sort by date (newest first)
    processed_articles.sort(key=lambda x: dt.datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
    
    return jsonify({
        'articles': processed_articles,
        'count': len(processed_articles)
    })

@app.route('/api/analytics/<company_name>')
def get_analytics(company_name):
    """API endpoint to get historical ESG scores for analytics"""
    df = load_esg_data()
    
    if df.empty or company_name not in df['company'].values:
        return jsonify({'error': 'Company not found'}), 404
    
    # Generate historical data with simulated changes based on news impact
    # In a real app, this would come from a database with historical records
    
    # Get current scores
    current_scores = calculate_category_scores(df, company_name)
    
    # Simulate historical data (in production, this would be from a database)
    historical_data = []
    
    if company_name == 'Nike':
        historical_data = [
            {"date": "2024-01-01", "environmental": 3.2, "social": 3.5, "governance": 3.8},
            {"date": "2024-01-15", "environmental": 3.3, "social": 3.5, "governance": 3.8},
            {"date": "2024-02-01", "environmental": 3.4, "social": 3.6, "governance": 3.9},
            {"date": "2024-02-15", "environmental": 3.5, "social": 3.6, "governance": 3.9},
            {"date": "2024-03-01", "environmental": 3.6, "social": 3.7, "governance": 4.0},
            {"date": "2024-03-05", "environmental": 3.7, "social": 3.7, "governance": 4.0},
            {"date": "2024-03-08", "environmental": 3.8, "social": 3.7, "governance": 4.0},
        ]
    elif company_name == 'Adidas':
        historical_data = [
            {"date": "2024-01-01", "environmental": 3.0, "social": 3.2, "governance": 3.5},
            {"date": "2024-01-15", "environmental": 3.1, "social": 3.2, "governance": 3.5},
            {"date": "2024-02-01", "environmental": 3.2, "social": 3.3, "governance": 3.6},
            {"date": "2024-02-15", "environmental": 3.3, "social": 3.3, "governance": 3.6},
            {"date": "2024-03-01", "environmental": 3.4, "social": 3.2, "governance": 3.7},
            {"date": "2024-03-05", "environmental": 3.4, "social": 2.9, "governance": 3.7},
        ]
    else:
        # Default historical data for other companies
        historical_data = [
            {"date": "2024-01-01", "environmental": 3.0, "social": 3.0, "governance": 3.0},
            {"date": "2024-02-01", "environmental": 3.1, "social": 3.1, "governance": 3.1},
            {"date": "2024-03-01", "environmental": 3.2, "social": 3.2, "governance": 3.2},
        ]
    
    # Calculate overall scores
    for entry in historical_data:
        entry['overall'] = round((entry['environmental'] + entry['social'] + entry['governance']) / 3, 2)
    
    return jsonify({
        'company': company_name,
        'historical_data': historical_data
    })

@app.route('/health')
def health():
    """Health check endpoint for cloud hosting"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('FLASK_ENV') == 'development'))
