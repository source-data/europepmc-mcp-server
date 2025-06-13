#!/usr/bin/env python3
"""
Test correct query format for Fiona M Watt.
"""

import asyncio
import httpx
import json

async def test_correct_format():
    """Test the correct query format for Fiona M Watt."""
    
    print("🔍 Testing correct query format for Fiona M Watt")
    print("=" * 60)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Basic text search (we know this works)
        print("\n1️⃣ Basic text search: Fiona M Watt")
        try:
            params = {
                "query": "Fiona M Watt",
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
                    
                    # Show authors to verify it's the right Fiona Watt
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_names = [a.get('fullName', 'Unknown') for a in authors[:5]]
                        else:
                            author_names = [authors.get('fullName', 'Unknown')]
                        print(f"      Authors: {', '.join(author_names)}")
                        
                        # Check for EMBO affiliation
                        for author in (authors if isinstance(authors, list) else [authors]):
                            if isinstance(author, dict):
                                affiliation = author.get('affiliation', '')
                                if 'EMBO' in affiliation or 'embo' in affiliation.lower():
                                    print(f"      🎯 EMBO affiliation found: {affiliation}")
                    print()
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Recent papers only
        print("\n2️⃣ Recent Fiona M Watt papers (2020+)")
        try:
            params = {
                "query": "Fiona M Watt AND FIRST_PDATE:[2020 TO *]",
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
        
        # Test 3: With EMBO (without quotes)
        print("\n3️⃣ Fiona M Watt + EMBO (no quotes)")
        try:
            params = {
                "query": "Fiona M Watt AND EMBO",
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
        
        # Test 4: Try different author field formats
        print("\n4️⃣ Testing different AUTH formats")
        auth_tests = [
            ("AUTH:Watt", "Simple last name"),
            ("AUTH:(Watt)", "Last name in parentheses"),
            ("AUTH:Watt AND Fiona", "Last name + first name"),
            ("(AUTH:Watt) AND Fiona", "Complex query")
        ]
        
        for query, description in auth_tests:
            try:
                params = {
                    "query": query,
                    "resultType": "lite",
                    "pageSize": 5,
                    "format": "json"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                print(f"   {description}: {result.get('hitCount', 0)} publications")
                if result.get('hitCount', 0) > 0:
                    print(f"      Query: {query}")
            except Exception as e:
                print(f"   {description}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_correct_format())
