#!/usr/bin/env python3
"""
Direct test of EuropePMC MCP server for Fiona M Watt disambiguation.
"""

import asyncio
import json
from src.europepmc_server.server import EuropePMCClient, AuthorDisambiguator

async def test_fiona_watt_searches():
    """Test different search strategies for Fiona M Watt."""
    
    print("🔍 Testing EuropePMC MCP Server for Fiona M Watt")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        
        # Test 1: Basic name search
        print("\n1️⃣ Basic search: AUTH:\"Fiona Watt\"")
        try:
            result1 = await client.search_publications(
                query='AUTH:"Fiona Watt"',
                page_size=5,
                sort="date"
            )
            print(f"   Found: {result1.get('hitCount', 0)} publications")
            if 'resultList' in result1 and 'result' in result1['resultList']:
                for i, pub in enumerate(result1['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Search with "Watt FM" format
        print("\n2️⃣ Alternative format: AUTH:\"Watt FM\"")
        try:
            result2 = await client.search_publications(
                query='AUTH:"Watt FM"',
                page_size=5,
                sort="date"
            )
            print(f"   Found: {result2.get('hitCount', 0)} publications")
            if 'resultList' in result2 and 'result' in result2['resultList']:
                for i, pub in enumerate(result2['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Search with EMBO affiliation
        print("\n3️⃣ With EMBO affiliation: AUTH:\"Fiona Watt\" AND AFFILIATION:\"EMBO\"")
        try:
            result3 = await client.search_publications(
                query='AUTH:"Fiona Watt" AND AFFILIATION:"EMBO"',
                page_size=5,
                sort="date"
            )
            print(f"   Found: {result3.get('hitCount', 0)} publications")
            if 'resultList' in result3 and 'result' in result3['resultList']:
                for i, pub in enumerate(result3['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Search with King's College London
        print("\n4️⃣ With King's College: AUTH:\"Fiona Watt\" AND AFFILIATION:\"King's College London\"")
        try:
            result4 = await client.search_publications(
                query='AUTH:"Fiona Watt" AND AFFILIATION:"King\'s College London"',
                page_size=5,
                sort="date"
            )
            print(f"   Found: {result4.get('hitCount', 0)} publications")
            if 'resultList' in result4 and 'result' in result4['resultList']:
                for i, pub in enumerate(result4['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Recent publications only
        print("\n5️⃣ Recent papers (2020+): AUTH:\"Fiona Watt\" AND FIRST_PDATE:[2020 TO *]")
        try:
            result5 = await client.search_publications(
                query='AUTH:"Fiona Watt" AND FIRST_PDATE:[2020 TO *]',
                page_size=10,
                sort="date"
            )
            print(f"   Found: {result5.get('hitCount', 0)} publications")
            if 'resultList' in result5 and 'result' in result5['resultList']:
                for i, pub in enumerate(result5['resultList']['result'][:5]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 6: Test the disambiguation tool
        print("\n6️⃣ Testing AuthorDisambiguator")
        try:
            disambiguator = AuthorDisambiguator()
            
            # Get some publications for testing
            result = await client.search_publications(
                query='AUTH:"Fiona Watt"',
                page_size=10
            )
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                
                # Test disambiguation
                disambiguated = disambiguator.disambiguate_author_publications(
                    "Fiona Watt", publications, threshold=80
                )
                
                print(f"   Original publications: {len(publications)}")
                print(f"   After disambiguation: {len(disambiguated)}")
                
                for pub in disambiguated[:3]:
                    match_score = pub.get('best_match_score', 'N/A')
                    print(f"   • {pub.get('title', 'No title')[:60]}... (Score: {match_score})")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fiona_watt_searches())
