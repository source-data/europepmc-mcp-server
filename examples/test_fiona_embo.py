#!/usr/bin/env python3
"""
Test the EuropePMC MCP server for the specific search:
Author: Fiona M Watt
Affiliation: EMBO
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCClient, AuthorDisambiguator

async def test_fiona_watt_embo():
    """Test search for Fiona M Watt with EMBO affiliation."""
    
    print("🔬 Testing EuropePMC MCP Server")
    print("Author: Fiona M Watt")
    print("Affiliation: EMBO")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        
        # Test 1: Direct search with author and EMBO affiliation
        print("\n1️⃣ Search: AUTH:\"Fiona M Watt\" AND AFFILIATION:\"EMBO\"")
        try:
            result1 = await client.search_publications(
                query='AUTH:"Fiona M Watt" AND AFFILIATION:"EMBO"',
                page_size=10,
                result_type="lite",
                sort="date"
            )
            
            hit_count = result1.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if 'resultList' in result1 and 'result' in result1['resultList']:
                publications = result1['resultList']['result']
                print(f"   📄 Showing first {min(len(publications), 5)} results:")
                
                for i, pub in enumerate(publications[:5], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    journal = pub.get('journalInfo', {}).get('journal', {}).get('title', 'Unknown journal')
                    pmid = pub.get('pmid', 'No PMID')
                    
                    print(f"\n   {i}. {title}")
                    print(f"      📅 Date: {date}")
                    print(f"      📖 Journal: {journal}")
                    print(f"      🔗 PMID: {pmid}")
                    
                    # Show authors if available
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, list):
                            author_names = [a.get('fullName', 'Unknown') for a in authors[:3]]
                        else:
                            author_names = [authors.get('fullName', 'Unknown')]
                        print(f"      👥 Authors: {', '.join(author_names)}")
                        if len(authors) > 3:
                            print(f"           ... and {len(authors) - 3} more")
            else:
                print("   ❌ No results found in response")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Alternative search with different name format
        print("\n2️⃣ Search: AUTH:\"Watt FM\" AND AFFILIATION:\"EMBO\"")
        try:
            result2 = await client.search_publications(
                query='AUTH:"Watt FM" AND AFFILIATION:"EMBO"',
                page_size=10,
                result_type="lite",
                sort="date"
            )
            
            hit_count = result2.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications")
            
            if hit_count > 0 and 'resultList' in result2 and 'result' in result2['resultList']:
                publications = result2['resultList']['result']
                print(f"   📄 Showing first {min(len(publications), 3)} results:")
                
                for i, pub in enumerate(publications[:3], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"   {i}. {title[:80]}... ({date})")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Broader search without affiliation, then filter
        print("\n3️⃣ Search: AUTH:\"Fiona M Watt\" (broader search)")
        try:
            result3 = await client.search_publications(
                query='AUTH:"Fiona M Watt"',
                page_size=20,
                result_type="lite",
                sort="date"
            )
            
            hit_count = result3.get('hitCount', 0)
            print(f"   📊 Found: {hit_count} publications total")
            
            if 'resultList' in result3 and 'result' in result3['resultList']:
                publications = result3['resultList']['result']
                
                # Filter for EMBO-related publications
                embo_pubs = []
                for pub in publications:
                    # Check if EMBO appears in title, abstract, or author affiliations
                    title = pub.get('title', '').lower()
                    abstract = pub.get('abstractText', '').lower()
                    
                    if 'embo' in title or 'embo' in abstract:
                        embo_pubs.append(pub)
                        continue
                    
                    # Check author affiliations
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, dict):
                            authors = [authors]
                        
                        for author in authors:
                            affiliation = author.get('affiliation', '').lower()
                            if 'embo' in affiliation:
                                embo_pubs.append(pub)
                                break
                
                print(f"   🎯 EMBO-related publications: {len(embo_pubs)}")
                
                for i, pub in enumerate(embo_pubs[:3], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    print(f"   {i}. {title[:80]}... ({date})")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Use the author disambiguation feature
        print("\n4️⃣ Testing Author Disambiguation")
        try:
            # Get publications for disambiguation
            result = await client.search_publications(
                query='AUTH:"Fiona Watt"',
                page_size=30,
                result_type="lite"
            )
            
            if 'resultList' in result and 'result' in result['resultList']:
                publications = result['resultList']['result']
                
                # Use the disambiguator
                disambiguator = AuthorDisambiguator()
                disambiguated = disambiguator.disambiguate_author_publications(
                    "Fiona M Watt", publications, threshold=85
                )
                
                print(f"   📊 Original publications: {len(publications)}")
                print(f"   🎯 After disambiguation (≥85% match): {len(disambiguated)}")
                
                # Filter disambiguated results for EMBO
                embo_disambiguated = []
                for pub in disambiguated:
                    title = pub.get('title', '').lower()
                    abstract = pub.get('abstractText', '').lower()
                    
                    if 'embo' in title or 'embo' in abstract:
                        embo_disambiguated.append(pub)
                        continue
                    
                    # Check author affiliations
                    if 'authorList' in pub and 'author' in pub['authorList']:
                        authors = pub['authorList']['author']
                        if isinstance(authors, dict):
                            authors = [authors]
                        
                        for author in authors:
                            affiliation = author.get('affiliation', '').lower()
                            if 'embo' in affiliation:
                                embo_disambiguated.append(pub)
                                break
                
                print(f"   🏢 EMBO-related after disambiguation: {len(embo_disambiguated)}")
                
                for i, pub in enumerate(embo_disambiguated[:3], 1):
                    title = pub.get('title', 'No title')
                    date = pub.get('firstPublicationDate', 'No date')
                    score = pub.get('best_match_score', 'N/A')
                    print(f"   {i}. {title[:70]}... ({date}) [Score: {score}]")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_fiona_watt_embo())
