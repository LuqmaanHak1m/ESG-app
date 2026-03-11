import os
from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import datetime as dt
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')


def load_esg_data():
    """Load ESG scores from CSV"""
    try:
        df = pd.read_csv('./data/esg_scores.csv')
        return df
    except Exception as e:
        print(f"Error loading ESG data: {e}")
        return pd.DataFrame()

def load_articles_data():
    """Load articles with ESG scores from CSV"""
    try:
        df = pd.read_csv('./data/articles_scored.csv')
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading articles data: {e}")
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
    articles_df = load_articles_data()
    companies = articles_df['company_name'].unique().tolist() if not articles_df.empty else []
    companies.sort()
    return render_template('index.html', companies=companies)

@app.route('/all-news')
def all_news():
    """All news page"""
    articles_df = load_articles_data()
    companies = articles_df['company_name'].unique().tolist() if not articles_df.empty else []
    companies.sort()
    return render_template('all_news.html', companies=companies)

@app.route('/company/<company_name>')
def company_page(company_name):
    """Individual company page"""
    articles_df = load_articles_data()
    companies = articles_df['company_name'].unique().tolist() if not articles_df.empty else []
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
    articles_df = load_articles_data()
    companies = articles_df['company_name'].unique().tolist() if not articles_df.empty else []
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

@app.route('/api/company/<company_name>')
def get_company_data(company_name):
    """API endpoint to get company ESG data"""
    print(f"\n=== GET /api/company/{company_name} ===")
    
    try:
        df = load_esg_data()
        articles_df = load_articles_data()
        
        print(f"ESG data loaded: {len(df)} rows")
        print(f"Articles data loaded: {len(articles_df)} rows")
        
        if articles_df.empty:
            print("ERROR: Articles dataframe is empty")
            return jsonify({'error': 'No data available'}), 404
        
        # Check if company exists in articles data (case-insensitive)
        print(f"Looking for company: '{company_name}'")
        print(f"Available companies: {articles_df['company_name'].unique().tolist()}")
        
        company_articles = articles_df[articles_df['company_name'].str.lower() == company_name.lower()]
        print(f"Found {len(company_articles)} articles for {company_name}")
        
        if company_articles.empty:
            print(f"ERROR: No articles found for company '{company_name}'")
            return jsonify({'error': 'Company not found'}), 404
        
        # Get the correct company name from the data
        correct_company_name = company_articles.iloc[0]['company_name']
        print(f"Using correct company name: '{correct_company_name}'")
        
        # Try to get ESG scores if available
        categories = {}
        if not df.empty:
            # Check for ESG data case-insensitively
            esg_company = None
            for company in df['company'].unique():
                if company.lower() == correct_company_name.lower():
                    esg_company = company
                    break
            
            if esg_company:
                print(f"Found ESG data for {esg_company} (matched from {correct_company_name})")
                categories = calculate_category_scores(df, esg_company)
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
            # Create default categories if no ESG data available
            categories = {
                'Environmental': {'score': 0, 'metrics': []},
                'Social': {'score': 0, 'metrics': []},
                'Governance': {'score': 0, 'metrics': []}
            }
        
        # Convert articles to the format expected by process_article_data
        articles_list = []
        for _, row in company_articles.iterrows():
            # Handle NaN values
            title = row['title'] if pd.notna(row['title']) else 'Unknown Article'
            summary = row['introduction'] if pd.notna(row['introduction']) else ''
            
            article = {
                'company': row['company_name'],
                'title': title,
                'summary': summary,
                'date': row['date'].strftime("%Y-%m-%d") if pd.notna(row['date']) else '',
                'climate_transition': float(row['climate_transition']) if pd.notna(row['climate_transition']) else 0.0,
                'energy_resource': float(row['energy_resource']) if pd.notna(row['energy_resource']) else 0.0,
                'biodiversity': float(row['biodiversity']) if pd.notna(row['biodiversity']) else 0.0,
                'water_use': float(row['water_use']) if pd.notna(row['water_use']) else 0.0,
                'waste_pollution': float(row['waste_pollution']) if pd.notna(row['waste_pollution']) else 0.0,
                'labour_relations': float(row['labour_relations']) if pd.notna(row['labour_relations']) else 0.0,
                'health_safety': float(row['health_safety']) if pd.notna(row['health_safety']) else 0.0,
                'human_rights_community': float(row['human_rights_community']) if pd.notna(row['human_rights_community']) else 0.0,
                'board_management': float(row['board_management']) if pd.notna(row['board_management']) else 0.0,
                'shareholder_rights': float(row['shareholder_rights']) if pd.notna(row['shareholder_rights']) else 0.0,
                'conduct_anti_corruption': float(row['conduct_anti_corruption']) if pd.notna(row['conduct_anti_corruption']) else 0.0,
                'tax_transparency_accounting': float(row['tax_transparency_accounting']) if pd.notna(row['tax_transparency_accounting']) else 0.0,
            }
            articles_list.append(article)
        
        print(f"Converted {len(articles_list)} articles to list format")
        
        # Process articles and calculate adjusted scores
        processed_articles = process_article_data(articles_list)
        print(f"Processed {len(processed_articles)} articles")
        
        adjusted_scores = calculate_adjusted_scores(categories, processed_articles, correct_company_name)
        print(f"Calculated adjusted scores: {list(adjusted_scores.keys())}")
        
        response = {
            'company': correct_company_name,
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
    articles_df = load_articles_data()
    
    if articles_df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    # Convert articles to the format expected by process_article_data
    articles_list = []
    for _, row in articles_df.iterrows():
        # Handle NaN values
        title = row['title'] if pd.notna(row['title']) else 'Unknown Article'
        summary = row['introduction'] if pd.notna(row['introduction']) else ''
        
        article = {
            'company': row['company_name'],
            'title': title,
            'summary': summary,
            'date': row['date'].strftime("%Y-%m-%d") if pd.notna(row['date']) else '',
            'climate_transition': float(row['climate_transition']) if pd.notna(row['climate_transition']) else 0.0,
            'energy_resource': float(row['energy_resource']) if pd.notna(row['energy_resource']) else 0.0,
            'biodiversity': float(row['biodiversity']) if pd.notna(row['biodiversity']) else 0.0,
            'water_use': float(row['water_use']) if pd.notna(row['water_use']) else 0.0,
            'waste_pollution': float(row['waste_pollution']) if pd.notna(row['waste_pollution']) else 0.0,
            'labour_relations': float(row['labour_relations']) if pd.notna(row['labour_relations']) else 0.0,
            'health_safety': float(row['health_safety']) if pd.notna(row['health_safety']) else 0.0,
            'human_rights_community': float(row['human_rights_community']) if pd.notna(row['human_rights_community']) else 0.0,
            'board_management': float(row['board_management']) if pd.notna(row['board_management']) else 0.0,
            'shareholder_rights': float(row['shareholder_rights']) if pd.notna(row['shareholder_rights']) else 0.0,
            'conduct_anti_corruption': float(row['conduct_anti_corruption']) if pd.notna(row['conduct_anti_corruption']) else 0.0,
            'tax_transparency_accounting': float(row['tax_transparency_accounting']) if pd.notna(row['tax_transparency_accounting']) else 0.0,
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
    df = load_esg_data()
    articles_df = load_articles_data()
    
    if articles_df.empty:
        return jsonify({'error': 'No data available'}), 404
    
    # Get articles for this company (case-insensitive)
    company_articles = articles_df[articles_df['company_name'].str.lower() == company_name.lower()].copy()
    
    if company_articles.empty:
        return jsonify({'error': 'Company not found'}), 404
    
    # Get the correct company name from the data
    correct_company_name = company_articles.iloc[0]['company_name']
    
    # Get current scores if available
    current_scores = {}
    if not df.empty:
        # Check for ESG data case-insensitively
        esg_company = None
        for company in df['company'].unique():
            if company.lower() == correct_company_name.lower():
                esg_company = company
                break
        
        if esg_company:
            print(f"Found ESG data for {esg_company} (matched from {correct_company_name})")
            current_scores = calculate_category_scores(df, esg_company)
        else:
            print(f"No ESG data found for {correct_company_name}, using defaults")
    
    # Sort by date
    company_articles = company_articles.sort_values('date')
    
    # Generate historical data by accumulating article impacts over time
    historical_data = []
    
    # Get date range
    min_date = company_articles['date'].min()
    max_date = company_articles['date'].max()
    
    # Create baseline scores from current ESG data or defaults
    baseline_env = current_scores.get('Environmental', {}).get('score', 3.0)
    baseline_social = current_scores.get('Social', {}).get('score', 3.0)
    baseline_gov = current_scores.get('Governance', {}).get('score', 3.0)
    
    # Generate data points at regular intervals
    current_date = min_date
    env_score = baseline_env - 0.5  # Start slightly lower
    social_score = baseline_social - 0.5
    gov_score = baseline_gov - 0.5
    
    while current_date <= max_date:
        # Get articles up to this date
        articles_to_date = company_articles[company_articles['date'] <= current_date]
        
        # Calculate cumulative impact
        env_impact = articles_to_date['environmental'].sum()
        social_impact = articles_to_date['social'].sum()
        gov_impact = articles_to_date['governance'].sum()
        
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
        env_impact = company_articles['environmental'].sum()
        social_impact = company_articles['social'].sum()
        gov_impact = company_articles['governance'].sum()
        
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
        'company': correct_company_name,
        'historical_data': historical_data
    })

@app.route('/health')
def health():
    """Health check endpoint for cloud hosting"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(os.environ.get('FLASK_ENV') == 'development'))
