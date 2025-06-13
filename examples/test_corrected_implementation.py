#!/usr/bin/env python3
"""
Test the corrected EuropePMC implementation with proper search strategies.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only the client and disambiguator classes (not the MCP server)
from europepmc_server.server import EuropePMCClient, AuthorDisambiguator

async def test_corrected_implementation():
    """Test the corrected EuropePMC implementation for Fiona M Watt."""
    
    print("🎯 Testing Corrected EuropePMC Implementation")
    print("=" * 60)
    
    async with EuropePMCClient() as client:
        disambiguator = AuthorDisambiguator()
        
        # Test the progressive search strategy
        author_name = "Fiona Watt"
        additional_terms = "EMBO"
        
        print(f"\n🔍 Testing progressive search for: {author_name}")
        print(f"Additional terms: {additional_terms}")
        
        # Strategy 1: Free text search (documentation recommended)
        search_strategies = []
        search_strategies.append(author_name)
        
        # Strategy 2: Name variations
        name_parts = author_name.split()
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            search_strategies.extend([
                f"{last} {first}",      # Last first
                f"{last} {first[0]}",   # Last initial
                f"{first[0]} {last}"    # Initial last
            ])
        
        # Strategy 3: Add context terms (free text, not field-specific)
        if additional_terms:
            base_strategies = search_strategies.copy()
            for base_query in base_strategies:
                # Add context as free text, not as AFFILIATION field
                search_strategies.append(f"{base_query} {additional_terms}")
                
                # Try Boolean combinations
                if "EMBO" in additional_terms:
                    search_strategies.append(f"{base_query} (EMBO OR director)")
        
        # Strategy 4: Try with date filtering for recent papers
        search_strategies.append(f"{author_name} AND FIRST_PDATE:[2020 TO *]")
        
        print(f"\n📋 Search strategies to try ({len(search_strategies)}):")
        for i, strategy in enumerate(search_strategies, 1):
            print(f"   {i}. {strategy}")
        
        # Try each strategy
        best_result = None
        successful_query = None
        
        for i, query in enumerate(search_strategies, 1):
            try:
                print(f"\n🔄 Strategy {i}: {query}")
                
                result = await client.search_publications(
                    query=query,
                    result_type="lite",
                    page_size=10,
                    sort="date"
                )
                
                hit_count = result.get("hitCount", 0)
                print(f"   Results: {hit_count}")
                
                if hit_count > 0:
                    best_result = result
                    successful_query = query
                    print(f"   ✅ SUCCESS! Using this strategy.")
                    break
                else:
                    print(f"   ❌ No results")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        if not best_result:
            print(f"\n❌ No publications found for author: {author_name}")
            return
        
        # Extract publications from result
        publications = []
        if "resultList" in best_result and "result" in best_result["resultList"]:
            publications = best_result["resultList"]["result"]
        
        print(f"\n📚 Found {len(publications)} publications before disambiguation")
        
        # Show first few publications
        for i, pub in enumerate(publications[:3]):
            title = pub.get("title", "No title")
            date = pub.get("firstPublicationDate", "No date")
            print(f"   {i+1}. {title[:60]}... ({date})")
            
            # Show authors
            if "authorList" in pub and "author" in pub["authorList"]:
                authors = pub["authorList"]["author"]
                if isinstance(authors, list):
                    author_names = [a.get("fullName", "Unknown") for a in authors[:3]]
                else:
                    author_names = [authors.get("fullName", "Unknown")]
                print(f"      Authors: {', '.join(author_names)}")
        
        # Perform author disambiguation
        print(f"\n🎯 Performing author disambiguation (threshold: 80)")
        disambiguated_pubs = disambiguator.disambiguate_author_publications(
            author_name, publications, threshold=80
        )
        
        print(f"📊 After disambiguation: {len(disambiguated_pubs)} publications")
        
        # Show disambiguated results
        if disambiguated_pubs:
            print(f"\n🎯 Top disambiguated publications:")
            for i, pub in enumerate(disambiguated_pubs[:5]):
                title = pub.get("title", "No title")
                date = pub.get("firstPublicationDate", "No date")
                score = pub.get("best_match_score", "N/A")
                matched_author = pub.get("author_matches", [])
                
                print(f"\n   {i+1}. {title}")
                print(f"      Date: {date}")
                print(f"      Match Score: {score}")
                if matched_author:
                    print(f"      Matched Author: {matched_author[0][0]} (score: {matched_author[0][1]})")
                
                # Show journal
                journal_info = pub.get("journalInfo", {})
                if journal_info and "journal" in journal_info:
                    journal_title = journal_info["journal"].get("title", "Unknown")
                    print(f"      Journal: {journal_title}")
        
        # Summary
        print(f"\n📈 SUMMARY:")
        print(f"   Successful query: {successful_query}")
        print(f"   Total strategies tried: {len(search_strategies)}")
        print(f"   Publications found: {len(publications)}")
        print(f"   After disambiguation: {len(disambiguated_pubs)}")
        print(f"   Success rate: {len(disambiguated_pubs)/len(publications)*100:.1f}%" if publications else "0%")

if __name__ == "__main__":
    asyncio.run(test_corrected_implementation())
