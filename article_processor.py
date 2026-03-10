import json
from app import process_article_data, calculate_adjusted_scores, calculate_category_scores, load_esg_data

def example_single_article():
    """Example with single article"""
    article_data = {
        "company": "Nike",
        "title": "Mitsui Signs Solar VPPA With NIKE Japan to Deliver 100% Renewable Power Across Operations",
        "climate_transition": 1.0,
        "energy_resource": 1.2
    }
    
    processed = process_article_data(article_data)
    print("Single Article Processing:")
    print(json.dumps(processed, indent=2))
    return processed

def example_multiple_articles():
    """Example with multiple articles"""
    articles_data = [
        {
            "company": "Nike",
            "title": "Mitsui Signs Solar VPPA With NIKE Japan to Deliver 100% Renewable Power Across Operations",
            "climate_transition": 1.0,
            "energy_resource": 1.2,
            "summary": "Nike Japan commits to 100% renewable energy through solar power agreement"
        },
        {
            "company": "Nike", 
            "title": "Nike Faces Labor Dispute at Indonesian Factory",
            "labour_relations": -0.8,
            "health_safety": -0.5,
            "human_rights_community": -0.3,
            "summary": "Workers at Nike supplier factory report poor working conditions"
        },
        {
            "company": "Adidas",
            "title": "Adidas Launches Circular Economy Initiative",
            "waste_pollution": 0.9,
            "climate_transition": 0.6,
            "biodiversity": 0.4,
            "summary": "Adidas announces plan to eliminate waste through circular design principles"
        }
    ]
    
    processed = process_article_data(articles_data)
    print("\nMultiple Articles Processing:")
    print(json.dumps(processed, indent=2))
    return processed

def example_full_integration():
    """Example showing full integration with ESG scores"""
    # Load original ESG data
    df = load_esg_data()
    original_categories = calculate_category_scores(df, "Nike")
    
    # Process articles
    articles_data = [
        {
            "company": "Nike",
            "title": "Nike Renewable Energy Partnership",
            "climate_transition": 1.0,
            "energy_resource": 1.2
        },
        {
            "company": "Nike",
            "title": "Nike Labor Issues Investigation", 
            "labour_relations": -0.6,
            "health_safety": -0.4
        }
    ]
    
    processed_articles = process_article_data(articles_data)
    adjusted_scores = calculate_adjusted_scores(original_categories, processed_articles, "Nike")
    
    print("\nFull Integration Example:")
    print("Original Environmental Score:", original_categories['Environmental']['score'])
    print("Adjusted Environmental Score:", adjusted_scores['Environmental']['score'])
    print("Environmental Change:", adjusted_scores['Environmental']['change'])
    
    print("\nOriginal Social Score:", original_categories['Social']['score'])
    print("Adjusted Social Score:", adjusted_scores['Social']['score'])
    print("Social Change:", adjusted_scores['Social']['change'])
    
    return {
        'original': original_categories,
        'adjusted': adjusted_scores,
        'articles': processed_articles
    }

def api_format_example():
    """Example of data format for API calls"""
    api_payload = {
        "articles": [
            {
                "company": "Nike",
                "title": "Nike Commits to Carbon Neutrality by 2030",
                "climate_transition": 1.5,
                "energy_resource": 0.8,
                "waste_pollution": 0.4,
                "summary": "Nike announces comprehensive carbon neutrality plan"
            },
            {
                "company": "Adidas", 
                "title": "Adidas Board Adds Sustainability Expert",
                "board_management": 0.6,
                "conduct_anti_corruption": 0.3,
                "date": "2024-03-09",
                "summary": "New board appointment focuses on ESG governance"
            }
        ]
    }
    
    print("\nAPI Payload Format:")
    print(json.dumps(api_payload, indent=2))
    
    # Process the articles
    processed = process_article_data(api_payload["articles"])
    print("\nProcessed Result:")
    print(json.dumps(processed, indent=2))
    
    return api_payload

if __name__ == "__main__":
    print("=== Article Processing Examples ===")
    
    # Run examples
    example_single_article()
    example_multiple_articles() 
    example_full_integration()
    api_format_example()
    
    print("\n=== Usage Instructions ===")
    print("1. Single article: pass dict directly to process_article_data()")
    print("2. Multiple articles: pass list of dicts to process_article_data()")
    print("3. API endpoint: POST to /api/process-articles with JSON payload")
    print("4. Integration: use calculate_adjusted_scores() with processed articles")