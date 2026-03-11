import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import datetime as dt
from datetime import datetime, timedelta

app = Flask(__name__)

load_dotenv()
# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['ENV'] = os.environ.get('FLASK_ENV')
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def load_esg_data():
    """Load ESG scores from database"""
    try:
        conn = get_db_connection()
        if not conn:
            print("ERROR: Could not connect to database")
            return []
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT company, category, metric, score
            FROM esg_scores
            ORDER BY company, category, metric
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"Loaded {len(rows)} ESG records from database")
        return rows
    except Exception as e:
        print(f"Error loading ESG data: {e}")
        return []

def load_articles_data():
    """Load articles with ESG scores from database"""
    try:
        conn = get_db_connection()
        if not conn:
            print("ERROR: Could not connect to database")
            return []
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                a.id,
                a.company_name,
                a.source,
                a.title,
                a.introduction,
                a.published_at as date,
                a.url,
                COALESCE(s.environmental, 0) as environmental,
                COALESCE(s.social, 0) as social,
                COALESCE(s.governance, 0) as governance,
                COALESCE(s.climate_transition, 0) as climate_transition,
                COALESCE(s.energy_resource, 0) as energy_resource,
                COALESCE(s.biodiversity, 0) as biodiversity,
                COALESCE(s.water_use, 0) as water_use,
                COALESCE(s.waste_pollution, 0) as waste_pollution,
                COALESCE(s.labour_relations, 0) as labour_relations,
                COALESCE(s.health_safety, 0) as health_safety,
                COALESCE(s.human_rights_community, 0) as human_rights_community,
                COALESCE(s.board_management, 0) as board_management,
                COALESCE(s.shareholder_rights, 0) as shareholder_rights,
                COALESCE(s.conduct_anti_corruption, 0) as conduct_anti_corruption,
                COALESCE(s.tax_transparency_accounting, 0) as tax_transparency_accounting
            FROM articles a
            LEFT JOIN article_scores s ON a.id = s.article_id
            ORDER BY a.published_at DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"Loaded {len(rows)} articles from database")
        return rows
    except Exception as e:
        print(f"Error loading articles data: {e}")
        return []

def calculate_category_scores(esg_data, company):
    """Calculate average scores by category for a company"""
    # Filter data for this company
    company_data = [row for row in esg_data if row['company'].lower() == company.lower()]
    
    categories = {}
    for category in ['Environmental', 'Social', 'Governance']:
        cat_data = [row for row in company_data if row['category'] == category]
        if cat_data:
            scores = [float(row['score']) for row in cat_data]
            avg_score = sum(scores) / len(scores)
            categories[category] = {
                'score': round(avg_score, 2),
                'metrics': [{'metric': row['metric'], 'score': float(row['score'])} for row in cat_data]
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
            'url': article.get('url', ''),
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
            original_score = float(metric['score'])
            
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
        if len(adjusted_metrics) > 0:
            adjusted_avg = sum(m['adjusted_score'] for m in adjusted_metrics) / len(adjusted_metrics)
            change = round(total_adjustment / len(adjusted_metrics), 2)
        else:
            adjusted_avg = category_data['score']
            change = 0
        
        adjusted_categories[category] = {
            'score': round(adjusted_avg, 2),
            'change': change
        }
    
    return adjusted_categories

@app.route('/')
def index():
    """Home page"""
    articles_data = load_articles_data()
    companies = list(set([row['company_name'] for row in articles_data]))
    companies = [c.capitalize() for c in companies]
    companies.sort()
    return render_template('index.html', companies=companies)

@app.route('/all-news')
def all_news():
    """All news page"""
    articles_data = load_articles_data()
    companies = list(set([row['company_name'] for row in articles_data]))
    companies = [c.capitalize() for c in companies]
    companies.sort()
    return render_template('all_news.html', companies=companies)

@app.route('/company/<company_name>')
def company_page(company_name):
    """Individual company page"""
    articles_data = load_articles_data()
    companies = list(set([row['company_name'] for row in articles_data]))
    companies = [c.capitalize() for c in companies]
    companies.sort()
    
    # Find the correct company name (case-insensitive)
    correct_company_name = None
    for company in companies:
        if company.lower() == company_name.lower():
            correct_company_name = company
            break
    
    if correct_company_name is None:
        return "Company not found", 404
    
    return render_template('company.html', company=correct_company_name, companies=companies)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    articles_data = load_articles_data()
    companies = list(set([row['company_name'] for row in articles_data]))
    companies = [c.capitalize() for c in companies]
    companies.sort()
    selected_company = request.args.get('company', '')
    return render_template('analytics.html', companies=companies, selected_company=selected_company)

@app.route('/analytics/<company_name>')
def analytics_for_company(company_name):
    """Analytics page"""
    df = load_esg_data()
    companies = df['company'].unique().tolist() if not df.empty else []

    get_analytics(company_name)

    return render_template('analytics.html', companies=companies)

@app.route('/risk-assessment')
def risk_assessment():
    """ESG Risk Assessment page"""
    articles_data = load_articles_data()
    companies = list(set([row['company_name'] for row in articles_data]))
    companies = [c.capitalize() for c in companies]
    companies.sort()
    return render_template('risk_assessment.html', companies=companies)

@app.route('/api/company/<company_name>')
def get_company_data(company_name):
    """API endpoint to get company ESG data"""
    print(f"\n=== GET /api/company/{company_name} ===")
    
    try:
        esg_data = load_esg_data()
        articles_data = load_articles_data()
        
        print(f"ESG data loaded: {len(esg_data)} rows")
        print(f"Articles data loaded: {len(articles_data)} rows")
        
        if not articles_data:
            print("ERROR: Articles data is empty")
            return jsonify({'error': 'No data available'}), 404
        
        # Check if company exists in articles data (case-insensitive)
        print(f"Looking for company: '{company_name}'")
        available_companies = list(set([row['company_name'] for row in articles_data]))
        print(f"Available companies: {available_companies}")
        
        company_articles = [row for row in articles_data if row['company_name'].lower() == company_name.lower()]
        print(f"Found {len(company_articles)} articles for {company_name}")
        
        if not company_articles:
            print(f"ERROR: No articles found for company '{company_name}'")
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the correct company name from the data
        correct_company_name = company_articles[0]['company_name']
        print(f"Using correct company name: '{correct_company_name}'")
        
        # Try to get ESG scores if available
        categories = {}
        if esg_data:
            # Check for ESG data case-insensitively
            esg_company = None
            for row in esg_data:
                if row['company'].lower() == correct_company_name.lower():
                    esg_company = row['company']
                    break
            
            if esg_company:
                print(f"Found ESG data for {esg_company} (matched from {correct_company_name})")
                categories = calculate_category_scores(esg_data, esg_company)
                print(f"Categories: {list(categories.keys())}")
            else:
                print(f"No ESG data found for {correct_company_name}, using defaults")
                categories = {
                    'Environmental': {'score': 0, 'metrics': []},
                    'Social': {'score': 0, 'metrics': []},
                    'Governance': {'score': 0, 'metrics': []}
                }
        else:
            print(f"No ESG data found for {correct_company_name}, using defaults")
            categories = {
                'Environmental': {'score': 0, 'metrics': []},
                'Social': {'score': 0, 'metrics': []},
                'Governance': {'score': 0, 'metrics': []}
            }
        
        # Convert articles to the format expected by process_article_data
        articles_list = []
        for row in company_articles:
            # Handle None/null values
            title = row['title'] if row['title'] else 'Unknown Article'
            summary = row['introduction'] if row['introduction'] else ''
            
            article = {
                'company': row['company_name'].capitalize(),
                'title': title,
                'summary': summary,
                'date': row['date'].strftime("%Y-%m-%d") if isinstance(row['date'], datetime) else str(row['date']),
                'url': row['url'] if row['url'] else '',
                'climate_transition': float(row['climate_transition']) if row['climate_transition'] else 0.0,
                'energy_resource': float(row['energy_resource']) if row['energy_resource'] else 0.0,
                'biodiversity': float(row['biodiversity']) if row['biodiversity'] else 0.0,
                'water_use': float(row['water_use']) if row['water_use'] else 0.0,
                'waste_pollution': float(row['waste_pollution']) if row['waste_pollution'] else 0.0,
                'labour_relations': float(row['labour_relations']) if row['labour_relations'] else 0.0,
                'health_safety': float(row['health_safety']) if row['health_safety'] else 0.0,
                'human_rights_community': float(row['human_rights_community']) if row['human_rights_community'] else 0.0,
                'board_management': float(row['board_management']) if row['board_management'] else 0.0,
                'shareholder_rights': float(row['shareholder_rights']) if row['shareholder_rights'] else 0.0,
                'conduct_anti_corruption': float(row['conduct_anti_corruption']) if row['conduct_anti_corruption'] else 0.0,
                'tax_transparency_accounting': float(row['tax_transparency_accounting']) if row['tax_transparency_accounting'] else 0.0,
            }
            articles_list.append(article)
        
        print(f"Converted {len(articles_list)} articles to list format")
        print(f"Sample article URL: {articles_list[0].get('url') if articles_list else 'No articles'}")
        
        # Process articles and calculate adjusted scores
        processed_articles = process_article_data(articles_list)
        print(f"Processed {len(processed_articles)} articles")
        print(f"Sample processed article: {processed_articles[0] if processed_articles else 'No articles'}")
        
        adjusted_scores = calculate_adjusted_scores(categories, processed_articles, correct_company_name)
        print(f"Calculated adjusted scores: {list(adjusted_scores.keys())}")
        
        response = {
            'company': correct_company_name.capitalize(),
            'original_scores': categories,
            'adjusted_scores': adjusted_scores,
            'news_articles': processed_articles
        }
        
        print(f"SUCCESS: Returning data for {correct_company_name}")
        print(f"Response keys: {list(response.keys())}")
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR in get_company_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

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
    articles_data = load_articles_data()
    
    if not articles_data:
        return jsonify({'error': 'No data available'}), 404
    
    # Convert articles to the format expected by process_article_data
    articles_list = []
    for row in articles_data:
        # Handle None/null values
        title = row['title'] if row['title'] else 'Unknown Article'
        summary = row['introduction'] if row['introduction'] else ''
        
        article = {
            'company': row['company_name'].capitalize(),
            'title': title,
            'summary': summary,
            'date': row['date'].strftime("%Y-%m-%d") if isinstance(row['date'], datetime) else str(row['date']),
            'url': row['url'] if row['url'] else '',
            'climate_transition': float(row['climate_transition']) if row['climate_transition'] else 0.0,
            'energy_resource': float(row['energy_resource']) if row['energy_resource'] else 0.0,
            'biodiversity': float(row['biodiversity']) if row['biodiversity'] else 0.0,
            'water_use': float(row['water_use']) if row['water_use'] else 0.0,
            'waste_pollution': float(row['waste_pollution']) if row['waste_pollution'] else 0.0,
            'labour_relations': float(row['labour_relations']) if row['labour_relations'] else 0.0,
            'health_safety': float(row['health_safety']) if row['health_safety'] else 0.0,
            'human_rights_community': float(row['human_rights_community']) if row['human_rights_community'] else 0.0,
            'board_management': float(row['board_management']) if row['board_management'] else 0.0,
            'shareholder_rights': float(row['shareholder_rights']) if row['shareholder_rights'] else 0.0,
            'conduct_anti_corruption': float(row['conduct_anti_corruption']) if row['conduct_anti_corruption'] else 0.0,
            'tax_transparency_accounting': float(row['tax_transparency_accounting']) if row['tax_transparency_accounting'] else 0.0,
        }
        articles_list.append(article)
    
    # Process articles
    processed_articles = process_article_data(articles_list)
    
    # Sort by date (newest first)
    processed_articles.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
    
    return jsonify({
        'articles': processed_articles,
        'count': len(processed_articles)
    })

@app.route('/api/analytics/<company_name>')
def get_analytics(company_name):
    """API endpoint to get historical ESG scores for analytics"""
    esg_data = load_esg_data()
    articles_data = load_articles_data()
    
    if not articles_data:
        return jsonify({'error': 'No data available'}), 404
    
    # Get articles for this company (case-insensitive)
    company_articles = [row for row in articles_data if row['company_name'].lower() == company_name.lower()]
    
    if not company_articles:
        return jsonify({'error': 'Company not found'}), 404
    
    # Get the correct company name from the data
    correct_company_name = company_articles[0]['company_name']
    
    # Get current scores if available
    current_scores = {}
    if esg_data:
        # Check for ESG data case-insensitively
        esg_company = None
        for row in esg_data:
            if row['company'].lower() == correct_company_name.lower():
                esg_company = row['company']
                break
        
        if esg_company:
            print(f"Found ESG data for {esg_company} (matched from {correct_company_name})")
            current_scores = calculate_category_scores(esg_data, esg_company)
        else:
            print(f"No ESG data found for {correct_company_name}, using defaults")
    
    # Sort by date
    company_articles = sorted(company_articles, key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.fromisoformat(str(x['date'])))
    
    # Generate historical data by accumulating article impacts over time
    historical_data = []
    
    # Get date range
    min_date = company_articles[0]['date'] if isinstance(company_articles[0]['date'], datetime) else datetime.fromisoformat(str(company_articles[0]['date']))
    max_date = company_articles[-1]['date'] if isinstance(company_articles[-1]['date'], datetime) else datetime.fromisoformat(str(company_articles[-1]['date']))
    
    # Create baseline scores from current ESG data or defaults
    baseline_env = float(current_scores.get('Environmental', {}).get('score', 3.0))
    baseline_social = float(current_scores.get('Social', {}).get('score', 3.0))
    baseline_gov = float(current_scores.get('Governance', {}).get('score', 3.0))
    
    # Generate data points at regular intervals
    current_date = min_date
    env_score = baseline_env - 0.5  # Start slightly lower
    social_score = baseline_social - 0.5
    gov_score = baseline_gov - 0.5
    
    while current_date <= max_date:
        # Get articles up to this date
        articles_to_date = [row for row in company_articles if (row['date'] if isinstance(row['date'], datetime) else datetime.fromisoformat(str(row['date']))) <= current_date]
        
        # Calculate cumulative impact
        env_impact = sum(float(row['environmental'] or 0) for row in articles_to_date)
        social_impact = sum(float(row['social'] or 0) for row in articles_to_date)
        gov_impact = sum(float(row['governance'] or 0) for row in articles_to_date)
        
        # Calculate scores (clamped between 0 and 5)
        env_score = max(0, min(5, baseline_env - 0.5 + env_impact))
        social_score = max(0, min(5, baseline_social - 0.5 + social_impact))
        gov_score = max(0, min(5, baseline_gov - 0.5 + gov_impact))
        
        historical_data.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'environmental': round(env_score, 2),
            'social': round(social_score, 2),
            'governance': round(gov_score, 2),
            'overall': round((env_score + social_score + gov_score) / 3, 2)
        })
        
        # Move to next week
        current_date += timedelta(days=7)
    
    # Ensure we have the final date
    if not historical_data or historical_data[-1]['date'] != max_date.strftime("%Y-%m-%d"):
        env_impact = sum(float(row['environmental'] or 0) for row in company_articles)
        social_impact = sum(float(row['social'] or 0) for row in company_articles)
        gov_impact = sum(float(row['governance'] or 0) for row in company_articles)
        
        env_score = max(0, min(5, baseline_env - 0.5 + env_impact))
        social_score = max(0, min(5, baseline_social - 0.5 + social_impact))
        gov_score = max(0, min(5, baseline_gov - 0.5 + gov_impact))
        
        historical_data.append({
            'date': max_date.strftime("%Y-%m-%d"),
            'environmental': round(env_score, 2),
            'social': round(social_score, 2),
            'governance': round(gov_score, 2),
            'overall': round((env_score + social_score + gov_score) / 3, 2)
        })
    
    return jsonify({
        'company': correct_company_name.capitalize(),
        'historical_data': historical_data
    })

@app.route('/api/risk-assessment')
def get_risk_assessment():
    """API endpoint to get ESG risk assessment for all companies"""
    esg_data = load_esg_data()
    articles_data = load_articles_data()
    
    if not articles_data:
        return jsonify({'error': 'No data available'}), 404
    
    # Get unique companies
    companies = list(set([row['company_name'] for row in articles_data]))
    
    risk_data = []
    
    for company in companies:
        # Get ESG scores for this company
        company_esg = [row for row in esg_data if row['company'].lower() == company.lower()]
        
        # Calculate category averages
        categories = {}
        for category in ['Environmental', 'Social', 'Governance']:
            cat_data = [row for row in company_esg if row['category'] == category]
            if cat_data:
                scores = [float(row['score']) for row in cat_data]
                avg_score = sum(scores) / len(scores)
                categories[category] = round(avg_score, 2)
            else:
                categories[category] = 0.0
        
        # Calculate overall score
        overall_score = round((categories['Environmental'] + categories['Social'] + categories['Governance']) / 3, 2)
        
        # Determine risk status based on thresholds
        # Healthy: overall >= 3.5
        # Watchlist: 2.5 <= overall < 3.5
        # High Risk: overall < 2.5
        if overall_score >= 3.5:
            risk_status = 'Healthy'
            recommended_action = 'Continue Monitoring'
            status_class = 'healthy'
        elif overall_score >= 2.5:
            risk_status = 'Watchlist'
            recommended_action = 'Investigate'
            status_class = 'watchlist'
        else:
            risk_status = 'High Risk'
            recommended_action = 'Escalate'
            status_class = 'high-risk'
        
        risk_data.append({
            'company': company.capitalize(),
            'overall_score': overall_score,
            'environmental_score': categories['Environmental'],
            'social_score': categories['Social'],
            'governance_score': categories['Governance'],
            'risk_status': risk_status,
            'recommended_action': recommended_action,
            'status_class': status_class
        })
    
    # Sort by overall score (descending)
    risk_data.sort(key=lambda x: x['overall_score'], reverse=True)
    
    return jsonify({
        'companies': risk_data,
        'count': len(risk_data)
    })

@app.route('/health')
def health():
    """Health check endpoint for cloud hosting"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('FLASK_ENV') == 'development'))
