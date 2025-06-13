#!/usr/bin/env python3
"""
Detailed test to explore Fiona Watt publications and find EMBO connections.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCClient, AuthorDisambiguator

async def test_fiona_watt_detailed():
    """Detailed exploration of Fiona Watt publications."""
    
    print("🔬 Detailed EuropePMC Search for Fiona Watt")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        
        # Test different name variations
        name_variations = [
            "Fiona Watt",
            "Fiona M Watt", 
            "Watt F",
            "Watt FM",
            "F Watt",
            "F M Watt"
        ]
        
        all_publications = []
        
        for name in name_variations:
            print(f"\n🔍 Testing: AUTH:\"{name}\"")
            try:
                result = await client.search_publications(
                    query=f'AUTH:"{name}"',
                    page_size=50,
                    result_type="lite",
                    sort="date"
                )
                
                hit_count = result.get('hitCount', 0)
                print(f"   📊 Found: {hit_count} publications")
                
                if 'resultList' in result and 'result' in result['resultList']:
                    publications = result['resultList']['result']
                    all_publications.extend(publications)
                    
                    # Look for EMBO-related publications
                    embo_count = 0
                    for pub in publications:
                        title = pub.get('title', '').lower()
                        abstract = pub.get('abstractText', '').lower()
                        
                        # Check for EMBO in title or abstract
                        if 'embo' in title or 'embo' in abstract:
                            embo_count += 1
                            print(f"   🎯 EMBO mention: {pub.get('title', 'No title')[:80]}...")
                            continue
                        
                        # Check author affiliations
                        if 'authorList' in pub and 'author' in pub['authorList']:
                            authors = pub['authorList']['author']
                            if isinstance(authors, dict):
                                authors = [authors]
                            
                            for author in authors:
                                affiliation = author.get('affiliation', '').lower()
                                if 'embo' in affiliation:
                                    embo_count += 1
                                    print(f"   🏢 EMBO affiliation: {pub.get('title', 'No title')[:80]}...")
                                    print(f"       Affiliation: {author.get('affiliation', 'N/A')}")
                                    break
                    
                    if embo_count > 0:
                        print(f"   ✅ Found {embo_count} EMBO-related publications")
                    else:
                        print("   ❌ No EMBO-related publications found")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Remove duplicates and analyze all publications
        print(f"\n📚 Total publications collected: {len(all_publications)}")
        
        # Deduplicate by PMID
        unique_pubs = {}
        for pub in all_publications:
            pmid = pub.get('pmid')
            if pmid and pmid not in unique_pubs:
                unique_pubs[pmid] = pub
        
        print(f"📚 Unique publications: {len(unique_pubs)}")
        
        # Analyze all unique publications for EMBO connections
        print("\n🔍 Analyzing all publications for EMBO connections...")
        embo_publications = []
        
        for pmid, pub in unique_pubs.items():
            title = pub.get('title', '').lower()
            abstract = pub.get('abstractText', '').lower()
            
            embo_found = False
            embo_context = []
            
            # Check title and abstract
            if 'embo' in title:
                embo_found = True
                embo_context.append("title")
            if 'embo' in abstract:
                embo_found = True
                embo_context.append("abstract")
            
            # Check author affiliations
            if 'authorList' in pub and 'author' in pub['authorList']:
                authors = pub['authorList']['author']
                if isinstance(authors, dict):
                    authors = [authors]
                
                for author in authors:
                    affiliation = author.get('affiliation', '').lower()
                    if 'embo' in affiliation:
                        embo_found = True
                        embo_context.append(f"affiliation: {author.get('fullName', 'Unknown')}")
            
            if embo_found:
                pub['embo_context'] = embo_context
                embo_publications.append(pub)
        
        print(f"🎯 Publications with EMBO connections: {len(embo_publications)}")
        
        # Display EMBO-related publications
        if embo_publications:
            print("\n📄 EMBO-related publications:")
            for i, pub in enumerate(embo_publications[:10], 1):  # Show first 10
                title = pub.get('title', 'No title')
                date = pub.get('firstPublicationDate', 'No date')
                journal = pub.get('journalInfo', {}).get('journal', {}).get('title', 'Unknown journal')
                pmid = pub.get('pmid', 'No PMID')
                embo_context = pub.get('embo_context', [])
                
                print(f"\n{i}. {title}")
                print(f"   📅 Date: {date}")
                print(f"   📖 Journal: {journal}")
                print(f"   🔗 PMID: {pmid}")
                print(f"   🎯 EMBO context: {', '.join(embo_context)}")
                
                # Show authors
                if 'authorList' in pub and 'author' in pub['authorList']:
                    authors = pub['authorList']['author']
                    if isinstance(authors, list):
                        author_names = [a.get('fullName', 'Unknown') for a in authors[:5]]
                    else:
                        author_names = [authors.get('fullName', 'Unknown')]
                    print(f"   👥 Authors: {', '.join(author_names)}")
                    if isinstance(authors, list) and len(authors) > 5:
                        print(f"        ... and {len(authors) - 5} more")
        
        # Test the MCP server's search_author_publications tool
        print(f"\n🤖 Testing MCP server's search_author_publications tool...")
        try:
            # This simulates how the MCP server would handle the request
            from europepmc_server.server import EuropePMCServer
            
            server = EuropePMCServer()
            
            # Test the search_author_publications method
            args = {
                "author_name": "Fiona Watt",
                "additional_terms": "EMBO",
                "page_size": 25,
                "disambiguation_threshold": 80
            }
            
            result = await server._search_author_publications(args)
            print("   ✅ MCP server search_author_publications completed")
            
            # Parse the result
            if hasattr(result, 'content') and result.content:
                content = result.content[0].text
                data = json.loads(content)
                
                print(f"   📊 Query used: {data.get('query', 'N/A')}")
                print(f"   📊 Total found: {data.get('total_found', 0)}")
                print(f"   🎯 After disambiguation: {data.get('after_disambiguation', 0)}")
                
                if data.get('publications'):
                    print(f"   📄 Sample publications:")
                    for i, pub in enumerate(data['publications'][:3], 1):
                        title = pub.get('title', 'No title')
                        score = pub.get('best_match_score', 'N/A')
                        print(f"   {i}. {title[:70]}... [Score: {score}]")
            
        except Exception as e:
            print(f"   ❌ Error testing MCP server: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Detailed analysis completed!")
        
        if embo_publications:
            print(f"🎉 Found {len(embo_publications)} publications with EMBO connections!")
        else:
            print("❌ No publications with EMBO connections found.")

if __name__ == "__main__":
    asyncio.run(test_fiona_watt_detailed())
