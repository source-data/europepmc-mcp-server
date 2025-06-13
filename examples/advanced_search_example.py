#!/usr/bin/env python3
"""
Advanced Search Example for EuropePMC MCP Server

This example demonstrates the enhanced filtering capabilities including:
- Publication type filtering (exclude corrections, retractions, etc.)
- Enhanced time filtering with FIRST_PDATE
- Source filtering (MED, PMC, PPR, etc.)
- Open access and full text filtering

Usage:
    python examples/advanced_search_example.py
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from europepmc_server.server import EuropePMCServer

async def demonstrate_advanced_search():
    """Demonstrate advanced search capabilities with enhanced filtering."""
    
    print("🔬 EuropePMC MCP Server - Advanced Search Example")
    print("=" * 60)
    
    # Initialize the MCP server
    server = EuropePMCServer()
    
    # Initialize the client
    from europepmc_server.server import EuropePMCClient
    server.client = EuropePMCClient()
    
    # Example 1: Basic search with default exclusions
    print("\n1️⃣ Search with Default Exclusions")
    print("   Query: stem cells AND regeneration")
    print("   Excludes: corrections, retractions, errata (default)")
    
    try:
        args = {
            "query": "stem cells AND regeneration",
            "filters": {
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 3
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Sample publications:")
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('publication_date', 'No date')
                    print(f"   {i}. {title[:70]}... ({date})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 2: Time-filtered search
    print("\n2️⃣ Time-Filtered Search (Recent Publications)")
    print("   Query: CRISPR gene editing")
    print("   Date range: 2022-01-01 to 2024-12-31")
    
    try:
        args = {
            "query": "CRISPR gene editing",
            "filters": {
                "publication_date_from": "2022-01-01",
                "publication_date_to": "2024-12-31",
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 3,
            "sort": "date"
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Recent publications:")
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('publication_date', 'No date')
                    print(f"   {i}. {title[:70]}... ({date})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 3: Open access filtering
    print("\n3️⃣ Open Access + Full Text Filter")
    print("   Query: machine learning healthcare")
    print("   Filters: Open access only + Has full text")
    
    try:
        args = {
            "query": "machine learning healthcare",
            "filters": {
                "open_access_only": True,
                "has_full_text": True,
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 3
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Open access publications:")
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    is_oa = pub.get('is_open_access', False)
                    has_ft = pub.get('has_full_text', False)
                    print(f"   {i}. {title[:60]}... [OA: {is_oa}, FT: {has_ft}]")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 4: Source filtering
    print("\n4️⃣ Source Filtering (PubMed + PMC only)")
    print("   Query: COVID-19 vaccine")
    print("   Sources: MED (PubMed) and PMC only")
    
    try:
        args = {
            "query": "COVID-19 vaccine",
            "filters": {
                "source": ["MED", "PMC"],
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 3
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Publications from PubMed/PMC:")
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    source = pub.get('source', 'Unknown')
                    print(f"   {i}. [{source}] {title[:60]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 5: Combined filtering demonstration
    print("\n5️⃣ Combined Filtering Example")
    print("   Query: artificial intelligence")
    print("   Filters: Recent (2023+), Open access, Exclude editorials")
    
    try:
        args = {
            "query": "artificial intelligence",
            "filters": {
                "publication_date_from": "2023-01-01",
                "open_access_only": True,
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction", "editorial", "letter"]
            },
            "result_type": "lite",
            "page_size": 3,
            "sort": "date"
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            print(f"   🔍 Final query: {data.get('final_query', 'N/A')[:100]}...")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Filtered publications:")
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('publication_date', 'No date')
                    print(f"   {i}. {title[:60]}... ({date})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Advanced search examples completed!")
    print()
    print("🎉 Key Features Demonstrated:")
    print("   ✅ Publication type filtering (exclude corrections, retractions)")
    print("   ✅ Enhanced time filtering with FIRST_PDATE")
    print("   ✅ Source filtering (MED, PMC, PPR, etc.)")
    print("   ✅ Open access and full text filtering")
    print("   ✅ Combined filtering for precise results")
    print()
    print("📋 CLI Usage:")
    print("   python test_mcp_cli.py advanced_search \"your query\" --date_from \"2023-01-01\" --open_access_only")

if __name__ == "__main__":
    asyncio.run(demonstrate_advanced_search())
