#!/usr/bin/env python3
"""
Targeted test for Fiona M Watt's recent publications.
"""

import asyncio
import httpx
import json

async def test_fiona_targeted():
    """Get Fiona M Watt's recent publications with detailed info."""
    
    print("🔍 Targeted search for Fiona M Watt's recent publications")
    print("=" * 70)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Recent Fiona M Watt papers (2020+)
        print("\n1️⃣ Recent Fiona M Watt papers (2020+)")
        try:
            params = {
                "query": '"Fiona M Watt" AND FIRST_PDATE:[2020 TO *]',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:5]):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    journal = pub.get('journalInfo', {}).get('journal', {}).get('title', 'Unknown journal')
                    print(f"   {i+1}. {title}")
                    print(f"      Journal: {journal} ({date})")
                    
                    # Show authors
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_names = [a.get('fullName', 'Unknown') for a in authors[:5]]
                        else:
                            author_names = [authors.get('fullName', 'Unknown')]
                        print(f"      Authors: {', '.join(author_names)}")
                    print()
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Fiona M Watt + EMBO
        print("\n2️⃣ Fiona M Watt + EMBO")
        try:
            params = {
                "query": '"Fiona M Watt" AND EMBO',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"   {i+1}. {title} ({date})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Fiona M Watt + stem cell
        print("\n3️⃣ Fiona M Watt + stem cell")
        try:
            params = {
                "query": '"Fiona M Watt" AND "stem cell"',
                "resultType": "lite",
                "pageSize": 10,
                "format": "json",
                "sort": "date"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"   {i+1}. {title} ({date})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Try with author field variations
        print("\n4️⃣ Testing AUTH field variations")
        auth_variations = [
            'AUTH:"Watt FM"',
            'AUTH:"Fiona M Watt"',
            'AUTH:"F M Watt"',
            'AUTH:"Watt F"'
        ]
        
        for auth_query in auth_variations:
            try:
                params = {
                    "query": auth_query,
                    "resultType": "lite",
                    "pageSize": 5,
                    "format": "json",
                    "sort": "date"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                print(f"   {auth_query}: {result.get('hitCount', 0)} publications")
                if result.get('hitCount', 0) > 0 and 'resultList' in result and 'result' in result['resultList']:
                    pub = result['resultList']['result'][0]
                    title = pub.get('title', 'No title')[:60]
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"      Latest: {title}... ({date})")
            except Exception as e:
                print(f"   {auth_query}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_fiona_targeted())
