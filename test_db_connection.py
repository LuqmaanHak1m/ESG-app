#!/usr/bin/env python3
"""
Database Connection Test Utility

This script tests the connection to the PostgreSQL database and verifies
that the required tables and data are accessible.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    """Test basic database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    print(f"\nDatabase URL: {DATABASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✓ Connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_tables():
    """Test if required tables exist and have data"""
    print("\n" + "=" * 60)
    print("Checking Tables")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check for articles table
        print("\n1. Checking 'articles' table...")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM articles")
            count = cursor.fetchone()[0]
            print(f"   ✓ Table exists with {count} rows")
            
            # Show sample data
            cursor.execute("SELECT id, company_name, title, url FROM articles LIMIT 3")
            samples = cursor.fetchall()
            print(f"   Sample articles:")
            for row in samples:
                print(f"     - ID: {row[0]}, Company: {row[1]}, Title: {row[2][:50]}...")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Check for article_scores table
        print("\n2. Checking 'article_scores' table...")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM article_scores")
            count = cursor.fetchone()[0]
            print(f"   ✓ Table exists with {count} rows")
            
            # Show sample data
            cursor.execute("SELECT article_id, environmental, social, governance FROM article_scores LIMIT 3")
            samples = cursor.fetchall()
            print(f"   Sample scores:")
            for row in samples:
                print(f"     - Article ID: {row[0]}, E: {row[1]}, S: {row[2]}, G: {row[3]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Check for esg_scores table
        print("\n3. Checking 'esg_scores' table...")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM esg_scores")
            count = cursor.fetchone()[0]
            print(f"   ✓ Table exists with {count} rows")
            
            # Show sample data
            cursor.execute("SELECT company, category, metric, score FROM esg_scores LIMIT 5")
            samples = cursor.fetchall()
            print(f"   Sample ESG scores:")
            for row in samples:
                print(f"     - Company: {row[0]}, Category: {row[1]}, Metric: {row[2]}, Score: {row[3]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")

def test_queries():
    """Test key queries used by the Flask app"""
    print("\n" + "=" * 60)
    print("Testing Key Queries")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test articles with scores query
        print("\n1. Testing articles with scores query...")
        try:
            cursor.execute("""
                SELECT 
                    a.id,
                    a.company_name,
                    a.title,
                    a.url,
                    COALESCE(s.environmental, 0) as environmental,
                    COALESCE(s.social, 0) as social,
                    COALESCE(s.governance, 0) as governance
                FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                LIMIT 3
            """)
            rows = cursor.fetchall()
            print(f"   ✓ Query successful, returned {len(rows)} rows")
            for row in rows:
                print(f"     - {row['company_name']}: {row['title'][:40]}...")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test ESG scores query
        print("\n2. Testing ESG scores query...")
        try:
            cursor.execute("""
                SELECT company, category, metric, score
                FROM esg_scores
                LIMIT 5
            """)
            rows = cursor.fetchall()
            print(f"   ✓ Query successful, returned {len(rows)} rows")
            for row in rows:
                print(f"     - {row['company']}: {row['category']} - {row['metric']}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test company list
        print("\n3. Testing company list query...")
        try:
            cursor.execute("SELECT DISTINCT company_name FROM articles ORDER BY company_name")
            companies = cursor.fetchall()
            print(f"   ✓ Query successful, found {len(companies)} companies:")
            for row in companies:
                print(f"     - {row['company_name']}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  ESG Dashboard - Database Connection Test".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Test connection
    if not test_connection():
        print("\n" + "!" * 60)
        print("CRITICAL: Cannot connect to database!")
        print("!" * 60)
        print("\nPossible solutions:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check DATABASE_URL environment variable:")
        print(f"   Current: {DATABASE_URL}")
        print("3. Verify credentials and host/port are correct")
        print("4. Check firewall/network connectivity")
        sys.exit(1)
    
    # Test tables and queries
    test_tables()
    test_queries()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
