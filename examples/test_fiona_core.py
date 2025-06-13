#!/usr/bin/env python3
"""
Test Fiona Watt search with core result type to get full author information.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCClient

async def test_fiona_watt_core():
    """Test Fiona Watt search with detailed results."""
    
    print("🔬 Testing Fiona Watt with Core Results")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        
        # Test 1: Search "Fiona Watt" with core results
        print("\n1️⃣ Search: 'Fiona Watt' (core results)")
        try:
            result = await client.search_publications(
                query='Fiona Watt',
                page_size=10,
                result_type="core"  # Get full details including authors
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                print(f"   📄 Analyzing first {len(publications)} results for Fiona Watt:")
                
                fiona_publications = []
                
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    pmid = pub.get('pmid', 'No PMID')
                    
                    # Check authors
                    found_fiona = False
                    fiona_author_name = ""
                    
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, dict):
                            authors = [authors]
                        
                        for author in authors:
                            full_name = author.get('fullName', '').lower()
                            if 'fiona' in full_name and 'watt' in full_name:
                                found_fiona = True
                                fiona_author_name = author.get('fullName', 'Unknown')
                                
                                # Check for EMBO affiliation
                                affiliation = author.get('affiliation', '').lower()
                                has_embo = 'embo' in affiliation
                                
                                print(f"\n   🎯 {i}. FOUND FIONA WATT!")
                                print(f"      📄 Title: {title}")
                                print(f"      👤 Author: {fiona_author_name}")
                                print(f"      🏢 Affiliation: {author.get('affiliation', 'Not specified')}")
                                print(f"      📅 Date: {date}")
                                print(f"      🔗 PMID: {pmid}")
                                print(f"      🎯 EMBO connection: {'YES' if has_embo else 'NO'}")
                                
                                if has_embo:
                                    fiona_publications.append({
                                        'publication': pub,
                                        'author_name': fiona_author_name,
                                        'affiliation': author.get('affiliation', ''),
                                        'embo_connection': True
                                    })
                                else:
                                    fiona_publications.append({
                                        'publication': pub,
                                        'author_name': fiona_author_name,
                                        'affiliation': author.get('affiliation', ''),
                                        'embo_connection': False
                                    })
                                break
                
                print(f"\n   📊 Summary:")
                print(f"   • Total publications analyzed: {len(publications)}")
                print(f"   • Publications with Fiona Watt: {len(fiona_publications)}")
                print(f"   • Publications with EMBO connection: {sum(1 for p in fiona_publications if p['embo_connection'])}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Direct search for "Watt AND EMBO" with core results
        print("\n2️⃣ Search: 'Watt AND EMBO' (core results)")
        try:
            result = await client.search_publications(
                query='Watt AND EMBO',
                page_size=15,
                result_type="core"
            )
            
            hit_count = result.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                
                fiona_embo_pubs = []
                
                for i, pub in enumerate(publications, 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    pmid = pub.get('pmid', 'No PMID')
                    
                    # Check for Fiona Watt in authors
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, dict):
                            authors = [authors]
                        
                        for author in authors:
                            full_name = author.get('fullName', '').lower()
                            if 'fiona' in full_name and 'watt' in full_name:
                                affiliation = author.get('affiliation', '')
                                
                                print(f"\n   🎯 {i}. FIONA WATT + EMBO MATCH!")
                                print(f"      📄 Title: {title}")
                                print(f"      👤 Author: {author.get('fullName', 'Unknown')}")
                                print(f"      🏢 Affiliation: {affiliation}")
                                print(f"      📅 Date: {date}")
                                print(f"      🔗 PMID: {pmid}")
                                
                                fiona_embo_pubs.append({
                                    'title': title,
                                    'author': author.get('fullName', 'Unknown'),
                                    'affiliation': affiliation,
                                    'date': date,
                                    'pmid': pmid
                                })
                                break
                
                print(f"\n   📊 Fiona Watt publications with EMBO connection: {len(fiona_embo_pubs)}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Test the MCP server's search_author_publications tool
        print("\n3️⃣ Testing MCP Server Tool: search_author_publications")
        try:
            from europepmc_server.server import EuropePMCServer
            
            server = EuropePMCServer()
            server.client = client  # Use our existing client
            
            # Test the search_author_publications method
            args = {
                "author_name": "Fiona Watt",
                "additional_terms": "EMBO",
                "page_size": 20,
                "disambiguation_threshold": 75
            }
            
            result = await server._search_author_publications(args)
            print("   ✅ MCP server search_author_publications completed")
            
            # Parse the result
            if hasattr(result, 'content') and result.content:
                content = result.content[0].text
                try:
                    data = json.loads(content)
                    
                    print(f"   📊 Query used: {data.get('query', 'N/A')}")
                    print(f"   📊 Author searched: {data.get('author_searched', 'N/A')}")
                    print(f"   📊 Total found: {data.get('total_found', 0)}")
                    print(f"   🎯 After disambiguation: {data.get('after_disambiguation', 0)}")
                    
                    if data.get('publications'):
                        print(f"   📄 Publications found:")
                        for i, pub in enumerate(data['publications'][:5], 1):
                            title = pub.get('title', 'No title')
                            score = pub.get('best_match_score', 'N/A')
                            date = pub.get('firstPublicationDate', 'No date')
                            print(f"   {i}. {title[:70]}... [Score: {score}] ({date})")
                    else:
                        print("   📄 No publications in result")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decode error: {e}")
                    print(f"   Raw content: {content[:200]}...")
            else:
                print("   ❌ No content in result")
            
        except Exception as e:
            print(f"   ❌ Error testing MCP server: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Core results test completed!")

if __name__ == "__main__":
    asyncio.run(test_fiona_watt_core())
