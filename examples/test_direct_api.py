#!/usr/bin/env python3
"""
Direct test of EuropePMC API for Fiona M Watt disambiguation.
"""

import asyncio
import httpx
import json

async def test_fiona_watt_direct():
    """Test different search strategies for Fiona M Watt directly with EuropePMC API."""
    
    print("🔍 Testing EuropePMC API directly for Fiona M Watt")
    print("=" * 60)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Basic name search
        print("\n1️⃣ Basic search: AUTH:\"Fiona Watt\"")
        try:
            params = {
                "query": 'AUTH:"Fiona Watt"',
                "resultType": "lite",
                "pageSize": 5,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Search with "Watt FM" format
        print("\n2️⃣ Alternative format: AUTH:\"Watt FM\"")
        try:
            params = {
                "query": 'AUTH:"Watt FM"',
                "resultType": "lite",
                "pageSize": 5,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Search with EMBO affiliation
        print("\n3️⃣ With EMBO affiliation: AUTH:\"Fiona Watt\" AND AFFILIATION:\"EMBO\"")
        try:
            params = {
                "query": 'AUTH:"Fiona Watt" AND AFFILIATION:"EMBO"',
                "resultType": "lite",
                "pageSize": 5,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Search with King's College London
        print("\n4️⃣ With King's College: AUTH:\"Fiona Watt\" AND AFFILIATION:\"King's College London\"")
        try:
            params = {
                "query": 'AUTH:"Fiona Watt" AND AFFILIATION:"King\'s College London"',
                "resultType": "lite",
                "pageSize": 5,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Recent publications only (2020+)
        print("\n5️⃣ Recent papers (2020+): AUTH:\"Fiona Watt\" AND FIRST_PDATE:[2020 TO *]")
        try:
            params = {
                "query": 'AUTH:"Fiona Watt" AND FIRST_PDATE:[2020 TO *]',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:5]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 6: Try "Watt F" format
        print("\n6️⃣ Short format: AUTH:\"Watt F\"")
        try:
            params = {
                "query": 'AUTH:"Watt F"',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:5]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 7: Try with stem cell keywords
        print("\n7️⃣ With stem cell keywords: AUTH:\"Fiona Watt\" AND (\"stem cell\" OR \"epidermal\")")
        try:
            params = {
                "query": 'AUTH:"Fiona Watt" AND ("stem cell" OR "epidermal")',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date",
                "synonym": "true"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:5]):
                    print(f"   • {pub.get('title', 'No title')[:80]}... ({pub.get('firstPublicationDate', 'No date')})")
                    # Show authors for this one
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_names = [a.get('fullName', 'Unknown') for a in authors[:3]]
                        else:
                            author_names = [authors.get('fullName', 'Unknown')]
                        print(f"     Authors: {', '.join(author_names)}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fiona_watt_direct())
