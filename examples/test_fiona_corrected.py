#!/usr/bin/env python3
"""
Test Fiona M Watt search using correct EuropePMC syntax.
"""

import asyncio
import httpx
import json

async def test_fiona_corrected():
    """Test Fiona M Watt search using correct syntax patterns."""
    
    print("🎯 Testing Fiona M Watt with CORRECT EuropePMC syntax")
    print("=" * 70)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Use the working pattern we discovered
        print("\n1️⃣ Working pattern: AUTH:Watt AND Fiona")
        try:
            params = {
                "query": "AUTH:Watt AND Fiona",
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
                    print(f"   {i+1}. {title} ({date})")
                    
                    # Check authors for Fiona M Watt specifically
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            for author in authors:
                                if isinstance(author, dict):
                                    full_name = author.get('fullName', '').lower()
                                    if 'fiona' in full_name and 'watt' in full_name:
                                        print(f"      🎯 Found Fiona: {author.get('fullName')}")
                                        affiliation = author.get('affiliation', '')
                                        if affiliation:
                                            print(f"      🏢 Affiliation: {affiliation}")
                                        break
                    print()
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Try with quoted author format
        print("\n2️⃣ Quoted format: AUTH:\"Watt F\"")
        try:
            params = {
                "query": 'AUTH:"Watt F"',
                "resultType": "lite",
                "pageSize": 5,
                "format": "json",
                "sort": "date"
            }
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"   Found: {result.get('hitCount', 0)} publications")
            if 'resultList' in result and 'result' in result['resultList']:
                for i, pub in enumerate(result['resultList']['result'][:3]):
                    title = pub.get('title', 'No title')[:60]
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"   {i+1}. {title}... ({date})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Try with EMBO affiliation using correct syntax
        print("\n3️⃣ With EMBO affiliation: AUTH:Watt AND Fiona AND AFFILIATION:\"EMBO\"")
        try:
            params = {
                "query": 'AUTH:Watt AND Fiona AND AFFILIATION:"EMBO"',
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
                    
                    # Show author details
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            for author in authors:
                                if isinstance(author, dict):
                                    full_name = author.get('fullName', '').lower()
                                    if 'fiona' in full_name and 'watt' in full_name:
                                        print(f"      🎯 Fiona: {author.get('fullName')}")
                                        print(f"      🏢 Affiliation: {author.get('affiliation', 'N/A')}")
                                        break
                    print()
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Try with King's College
        print("\n4️⃣ With King's College: AUTH:Watt AND Fiona AND AFFILIATION:\"King's College\"")
        try:
            params = {
                "query": 'AUTH:Watt AND Fiona AND AFFILIATION:"King\'s College"',
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
        
        # Test 5: Recent papers with date filter
        print("\n5️⃣ Recent papers: AUTH:Watt AND Fiona AND FIRST_PDATE:[2020 TO *]")
        try:
            params = {
                "query": "AUTH:Watt AND Fiona AND FIRST_PDATE:[2020 TO *]",
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
                    journal = pub.get('journalInfo', {}).get('journal', {}).get('title', 'Unknown')
                    print(f"   {i+1}. {title}")
                    print(f"      Journal: {journal} ({date})")
                    print()
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fiona_corrected())
