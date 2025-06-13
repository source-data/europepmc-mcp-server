#!/usr/bin/env python3
"""
Test different EuropePMC field search syntax patterns.
"""

import asyncio
import httpx
import json

async def test_field_syntax():
    """Test different field search syntax patterns for EuropePMC."""
    
    print("🔍 Testing EuropePMC Field Search Syntax")
    print("=" * 60)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test different author field syntax patterns
        author_tests = [
            # Basic patterns
            ('AUTH:Smith', 'Basic last name'),
            ('AUTH:"Smith"', 'Quoted last name'),
            ('AUTH:Smith J', 'Last name + initial'),
            ('AUTH:"Smith J"', 'Quoted last name + initial'),
            ('AUTH:"Smith, J"', 'Quoted last name, initial'),
            
            # Full name patterns
            ('AUTH:"John Smith"', 'Quoted full name'),
            ('AUTH:John AND AUTH:Smith', 'Separate first/last'),
            ('AUTHOR:Smith', 'AUTHOR field'),
            ('AUTHOR:"Smith J"', 'Quoted AUTHOR field'),
            
            # Known working patterns from our tests
            ('AUTH:Watt', 'Known working: Watt'),
            ('AUTH:Watt AND Fiona', 'Known working: Watt + Fiona'),
        ]
        
        print("\n📝 Testing Author Field Syntax:")
        for query, description in author_tests:
            try:
                params = {
                    "query": query,
                    "resultType": "lite",
                    "pageSize": 1,
                    "format": "json"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                hit_count = result.get('hitCount', 0)
                status = "✅" if hit_count > 0 else "❌"
                print(f"   {status} {description}: {hit_count:,} results")
                print(f"      Query: {query}")
                
                # Show first result if available
                if hit_count > 0 and 'resultList' in result and 'result' in result['resultList']:
                    first_pub = result['resultList']['result'][0]
                    title = first_pub.get('title', 'No title')[:50]
                    print(f"      Sample: {title}...")
                print()
                
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
                print(f"      Query: {query}")
                print()
        
        # Test affiliation field syntax
        print("\n🏢 Testing Affiliation Field Syntax:")
        affiliation_tests = [
            ('AFFILIATION:Harvard', 'Basic affiliation'),
            ('AFFILIATION:"Harvard"', 'Quoted affiliation'),
            ('AFFILIATION:"Harvard University"', 'Quoted full affiliation'),
            ('AFF:Harvard', 'AFF field'),
            ('INST:Harvard', 'INST field'),
            ('ORG:Harvard', 'ORG field'),
        ]
        
        for query, description in affiliation_tests:
            try:
                params = {
                    "query": query,
                    "resultType": "lite",
                    "pageSize": 1,
                    "format": "json"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                hit_count = result.get('hitCount', 0)
                status = "✅" if hit_count > 0 else "❌"
                print(f"   {status} {description}: {hit_count:,} results")
                print(f"      Query: {query}")
                print()
                
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
                print(f"      Query: {query}")
                print()
        
        # Test combined author + affiliation
        print("\n🔗 Testing Combined Author + Affiliation:")
        combined_tests = [
            ('AUTH:Smith AND AFFILIATION:Harvard', 'AUTH + AFFILIATION'),
            ('AUTH:"Smith J" AND AFFILIATION:"Harvard"', 'Quoted AUTH + AFFILIATION'),
            ('(AUTH:Smith) AND (AFFILIATION:Harvard)', 'Parentheses'),
            ('AUTH:Smith AFFILIATION:Harvard', 'Space separated'),
        ]
        
        for query, description in combined_tests:
            try:
                params = {
                    "query": query,
                    "resultType": "lite",
                    "pageSize": 1,
                    "format": "json"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                hit_count = result.get('hitCount', 0)
                status = "✅" if hit_count > 0 else "❌"
                print(f"   {status} {description}: {hit_count:,} results")
                print(f"      Query: {query}")
                print()
                
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
                print(f"      Query: {query}")
                print()
        
        # Test date range syntax
        print("\n📅 Testing Date Range Syntax:")
        date_tests = [
            ('FIRST_PDATE:[2020 TO *]', 'Date range from 2020'),
            ('PUB_DATE:[2020 TO 2024]', 'PUB_DATE range'),
            ('PDATE:[2020 TO *]', 'PDATE range'),
            ('DATE:[2020 TO *]', 'DATE range'),
        ]
        
        for query, description in date_tests:
            try:
                params = {
                    "query": f"cancer AND {query}",  # Add cancer to limit results
                    "resultType": "lite",
                    "pageSize": 1,
                    "format": "json"
                }
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                hit_count = result.get('hitCount', 0)
                status = "✅" if hit_count > 0 else "❌"
                print(f"   {status} {description}: {hit_count:,} results")
                print(f"      Query: cancer AND {query}")
                print()
                
            except Exception as e:
                print(f"   ❌ {description}: Error - {e}")
                print(f"      Query: cancer AND {query}")
                print()

if __name__ == "__main__":
    asyncio.run(test_field_syntax())
