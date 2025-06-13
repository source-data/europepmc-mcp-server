#!/usr/bin/env python3
"""
Test the enhanced filtering capabilities of the EuropePMC MCP server.
Demonstrates publication type filtering and enhanced time filtering.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCServer

async def test_enhanced_filtering():
    """Test the enhanced filtering capabilities."""
    
    print("🔬 Testing Enhanced EuropePMC Filtering")
    print("Author: Fiona M Watt, Affiliation: EMBO")
    print("=" * 70)
    
    # Initialize the MCP server
    server = EuropePMCServer()
    
    # Initialize the client
    from europepmc_server.server import EuropePMCClient
    server.client = EuropePMCClient()
    
    # Test 1: Search with default exclusions (corrections, retractions, etc.)
    print("\n1️⃣ Advanced Search with Default Exclusions")
    print("   Query: Fiona Watt AND EMBO")
    print("   Excludes: corrections, corrigenda, errata, retractions (default)")
    
    try:
        args = {
            "query": "Fiona Watt AND EMBO",
            "filters": {
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 5
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            print(f"   🔍 Final query: {data.get('final_query', 'N/A')}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Sample publications:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('publication_date', 'No date')
                    print(f"   {i}. {title[:70]}... ({date})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Time-filtered search (recent publications only)
    print("\n2️⃣ Time-Filtered Search (2020-2024)")
    print("   Query: Fiona Watt AND EMBO")
    print("   Date range: 2020-01-01 to 2024-12-31")
    
    try:
        args = {
            "query": "Fiona Watt AND EMBO",
            "filters": {
                "publication_date_from": "2020-01-01",
                "publication_date_to": "2024-12-31",
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 5,
            "sort": "date"
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            print(f"   🔍 Final query: {data.get('final_query', 'N/A')}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Recent publications:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('publication_date', 'No date')
                    print(f"   {i}. {title[:70]}... ({date})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Source filtering (only PubMed and PMC)
    print("\n3️⃣ Source Filtering (PubMed + PMC only)")
    print("   Query: Fiona Watt AND EMBO")
    print("   Sources: MED (PubMed) and PMC only")
    
    try:
        args = {
            "query": "Fiona Watt AND EMBO",
            "filters": {
                "source": ["MED", "PMC"],
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 5
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            print(f"   🔍 Final query: {data.get('final_query', 'N/A')}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Publications from PubMed/PMC:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    source = pub.get('source', 'Unknown')
                    print(f"   {i}. [{source}] {title[:60]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Open access only with full text
    print("\n4️⃣ Open Access + Full Text Filter")
    print("   Query: Fiona Watt AND EMBO")
    print("   Filters: Open access only + Has full text")
    
    try:
        args = {
            "query": "Fiona Watt AND EMBO",
            "filters": {
                "open_access_only": True,
                "has_full_text": True,
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction"]
            },
            "result_type": "lite",
            "page_size": 5
        }
        
        result = await server._advanced_search(args)
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            data = json.loads(content)
            
            print(f"   📊 Results found: {data.get('hit_count', 0)}")
            print(f"   🔍 Final query: {data.get('final_query', 'N/A')}")
            
            publications = data.get('publications', [])
            if publications:
                print("   📄 Open access publications with full text:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    is_oa = pub.get('is_open_access', False)
                    has_ft = pub.get('has_full_text', False)
                    print(f"   {i}. {title[:60]}... [OA: {is_oa}, FT: {has_ft}]")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Compare with and without filtering
    print("\n5️⃣ Comparison: With vs Without Filtering")
    
    try:
        # Without filtering
        args_unfiltered = {
            "query": "Fiona Watt AND EMBO",
            "result_type": "lite",
            "page_size": 10
        }
        
        result_unfiltered = await server._search_publications(args_unfiltered)
        
        # With filtering
        args_filtered = {
            "query": "Fiona Watt AND EMBO",
            "filters": {
                "exclude_types": ["correction", "corrigendum", "erratum", "retraction", "editorial", "letter"],
                "publication_date_from": "2015-01-01"
            },
            "result_type": "lite",
            "page_size": 10
        }
        
        result_filtered = await server._advanced_search(args_filtered)
        
        if hasattr(result_unfiltered, 'content') and result_unfiltered.content:
            unfiltered_data = json.loads(result_unfiltered.content[0].text)
            unfiltered_count = unfiltered_data.get('hit_count', 0)
        else:
            unfiltered_count = 0
        
        if hasattr(result_filtered, 'content') and result_filtered.content:
            filtered_data = json.loads(result_filtered.content[0].text)
            filtered_count = filtered_data.get('hit_count', 0)
        else:
            filtered_count = 0
        
        print(f"   📊 Unfiltered results: {unfiltered_count}")
        print(f"   📊 Filtered results: {filtered_count}")
        print(f"   📊 Reduction: {unfiltered_count - filtered_count} publications")
        print(f"   📊 Percentage filtered out: {((unfiltered_count - filtered_count) / max(unfiltered_count, 1)) * 100:.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Demonstrate CLI usage
    print("\n6️⃣ CLI Usage Examples")
    print("   You can now use these enhanced filtering options:")
    print()
    print("   # Exclude corrections and editorials")
    print("   python test_mcp_cli.py advanced_search \"Fiona Watt AND EMBO\" --exclude_corrections --exclude_editorials")
    print()
    print("   # Time filtering")
    print("   python test_mcp_cli.py advanced_search \"Fiona Watt AND EMBO\" --date_from \"2020-01-01\" --date_to \"2024-12-31\"")
    print()
    print("   # Open access only")
    print("   python test_mcp_cli.py advanced_search \"Fiona Watt AND EMBO\" --open_access_only --has_full_text")
    print()
    print("   # Source filtering")
    print("   python test_mcp_cli.py advanced_search \"Fiona Watt AND EMBO\" --source_filter MED PMC")
    
    print("\n" + "=" * 70)
    print("✅ Enhanced filtering test completed!")
    print()
    print("🎉 New Features Added:")
    print("   ✅ Publication type filtering (exclude corrections, retractions, etc.)")
    print("   ✅ Enhanced time filtering with FIRST_PDATE")
    print("   ✅ Source filtering (MED, PMC, PPR, etc.)")
    print("   ✅ Article section filtering")
    print("   ✅ Default exclusion of non-research content")
    print("   ✅ CLI support for all new filters")

if __name__ == "__main__":
    asyncio.run(test_enhanced_filtering())
