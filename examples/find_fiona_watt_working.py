#!/usr/bin/env python3
"""
Working script to find Fiona M Watt's papers using the EuropePMC API.
"""

import asyncio
import httpx
import json

async def find_fiona_watt_papers():
    """Find Fiona M Watt's papers using working search strategies."""
    
    print("🔍 FINDING FIONA M WATT'S PAPERS")
    print("=" * 50)
    
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    
    # Strategy: Search for stem cell papers and then filter by author
    search_strategies = [
        # Single word searches that work
        "stem",
        "epidermal", 
        "keratinocyte",
        "EMBO",
        
        # Try author field with different formats
        "AUTH:Watt",
        "AUTHOR:Watt",
        
        # Try with quotes
        '"Fiona Watt"',
        '"Watt F"',
        '"F Watt"',
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        for i, query in enumerate(search_strategies, 1):
            try:
                print(f"\n{i}. Testing query: {query}")
                
                params = {
                    "query": query,
                    "resultType": "lite",
                    "pageSize": 10,
                    "format": "json",
                    "sort": "date"
                }
                
                response = await client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                result = response.json()
                
                hit_count = result.get("hitCount", 0)
                print(f"   Results: {hit_count}")
                
                if hit_count > 0:
                    # Look for Fiona Watt in the results
                    publications = result.get("resultList", {}).get("result", [])
                    
                    fiona_papers = []
                    for pub in publications:
                        author_string = pub.get("authorString", "").lower()
                        title = pub.get("title", "").lower()
                        
                        # Check if this could be Fiona Watt
                        if any(term in author_string for term in ["watt", "fiona"]) or \
                           any(term in title for term in ["watt", "fiona"]):
                            fiona_papers.append(pub)
                    
                    if fiona_papers:
                        print(f"   🎯 Found {len(fiona_papers)} potential Fiona Watt papers!")
                        for j, paper in enumerate(fiona_papers[:3]):
                            title = paper.get("title", "No title")
                            authors = paper.get("authorString", "No authors")
                            date = paper.get("firstPublicationDate", "No date")
                            print(f"      {j+1}. {title[:60]}...")
                            print(f"         Authors: {authors}")
                            print(f"         Date: {date}")
                        
                        if len(fiona_papers) >= 5:
                            print(f"\n✅ SUCCESS! Found {len(fiona_papers)} papers with query: {query}")
                            return fiona_papers[:5]
                    else:
                        print(f"   ❌ No Fiona Watt papers found in results")
                else:
                    print(f"   ❌ No results")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # If no specific Fiona Watt papers found, try a broader approach
        print(f"\n🔄 Trying broader stem cell search to find relevant papers...")
        
        try:
            params = {
                "query": "stem",
                "resultType": "lite", 
                "pageSize": 50,  # Get more results to search through
                "format": "json",
                "sort": "date"
            }
            
            response = await client.get(f"{base_url}/search", params=params)
            response.raise_for_status()
            result = response.json()
            
            publications = result.get("resultList", {}).get("result", [])
            print(f"   Searching through {len(publications)} stem cell papers...")
            
            # Look for any papers that might be by Fiona Watt
            potential_papers = []
            for pub in publications:
                author_string = pub.get("authorString", "").lower()
                title = pub.get("title", "").lower()
                
                # More flexible matching
                if "watt" in author_string or "watt" in title:
                    potential_papers.append(pub)
            
            if potential_papers:
                print(f"\n🎯 Found {len(potential_papers)} papers mentioning 'Watt'!")
                for i, paper in enumerate(potential_papers[:5]):
                    title = paper.get("title", "No title")
                    authors = paper.get("authorString", "No authors")
                    date = paper.get("firstPublicationDate", "No date")
                    journal = paper.get("journalTitle", "No journal")
                    print(f"\n   {i+1}. {title}")
                    print(f"      Authors: {authors}")
                    print(f"      Journal: {journal} ({date})")
                
                return potential_papers[:5]
            else:
                print(f"   ❌ No papers mentioning 'Watt' found")
                
        except Exception as e:
            print(f"   ❌ Error in broader search: {e}")
    
    print(f"\n❌ Could not find Fiona M Watt's papers")
    return []

async def main():
    papers = await find_fiona_watt_papers()
    
    if papers:
        print(f"\n🎉 FINAL RESULT: Found {len(papers)} papers!")
        print("=" * 50)
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   Authors: {paper.get('authorString', 'No authors')}")
            print(f"   Journal: {paper.get('journalTitle', 'No journal')}")
            print(f"   Date: {paper.get('firstPublicationDate', 'No date')}")
            print(f"   PMID: {paper.get('pmid', 'No PMID')}")
    else:
        print(f"\n❌ No papers found. This suggests either:")
        print("   1. Fiona M Watt's papers are not in EuropePMC")
        print("   2. We need to use a different search approach")
        print("   3. The name/affiliation details are different")

if __name__ == "__main__":
    asyncio.run(main())
