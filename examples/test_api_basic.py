#!/usr/bin/env python3
"""
Basic API test to verify EuropePMC is working and explore search strategies.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCClient

async def test_basic_api():
    """Test basic API functionality and search strategies."""
    
    print("🔬 Basic EuropePMC API Test")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        
        # Test 1: Basic search to verify API is working
        print("\n1️⃣ Testing basic search: 'cancer'")
        try:
            result = await client.search_publications(
                query='cancer',
                page_size=5,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                print(f"   📄 Sample results:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    print(f"   {i}. {title[:80]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Search for a known author (more common name)
        print("\n2️⃣ Testing author search: AUTH:\"Smith J\"")
        try:
            result = await client.search_publications(
                query='AUTH:"Smith J"',
                page_size=5,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Search without quotes
        print("\n3️⃣ Testing: Fiona Watt (without quotes)")
        try:
            result = await client.search_publications(
                query='Fiona Watt',
                page_size=10,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                print(f"   📄 Sample results:")
                for i, pub in enumerate(publications[:5], 1):
                    title = pub.get('title', 'No title')
                    authors = []
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        author_data = pub['authorList']['author']
                        if isinstance(author_data, list):
                            authors = [a.get('fullName', 'Unknown') for a in author_data[:3]]
                        else:
                            authors = [author_data.get('fullName', 'Unknown')]
                    
                    print(f"   {i}. {title[:60]}...")
                    print(f"      Authors: {', '.join(authors)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Search with partial name
        print("\n4️⃣ Testing: Watt (surname only)")
        try:
            result = await client.search_publications(
                query='AUTH:Watt',
                page_size=10,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                
                # Look for Fiona Watt specifically
                fiona_count = 0
                for pub in publications:
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, dict):
                            authors = [authors]
                        
                        for author in authors:
                            full_name = author.get('fullName', '').lower()
                            if 'fiona' in full_name and 'watt' in full_name:
                                fiona_count += 1
                                print(f"   🎯 Found Fiona Watt: {pub.get('title', 'No title')[:60]}...")
                                print(f"      Author: {author.get('fullName', 'Unknown')}")
                                print(f"      Date: {pub.get('firstPublicationDate', 'No date')}")
                                break
                
                print(f"   🎯 Publications with 'Fiona Watt': {fiona_count}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Search for EMBO publications
        print("\n5️⃣ Testing: EMBO")
        try:
            result = await client.search_publications(
                query='EMBO',
                page_size=10,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                print(f"   📄 Sample EMBO publications:")
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    print(f"   {i}. {title[:80]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Combined search
        print("\n6️⃣ Testing: Watt AND EMBO")
        try:
            result = await client.search_publications(
                query='Watt AND EMBO',
                page_size=10,
                result_type="lite"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                print(f"   📄 Results:")
                for i, pub in enumerate(publications[:5], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    
                    # Get authors
                    authors = []
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        author_data = pub['authorList']['author']
                        if isinstance(author_data, list):
                            authors = [a.get('fullName', 'Unknown') for a in author_data[:3]]
                        else:
                            authors = [author_data.get('fullName', 'Unknown')]
                    
                    print(f"\n   {i}. {title}")
                    print(f"      📅 Date: {date}")
                    print(f"      👥 Authors: {', '.join(authors)}")
                    
                    # Check for Fiona Watt
                    for author_name in authors:
                        if 'fiona' in author_name.lower() and 'watt' in author_name.lower():
                            print(f"      🎯 FOUND FIONA WATT: {author_name}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Basic API test completed!")

if __name__ == "__main__":
    asyncio.run(test_basic_api())
