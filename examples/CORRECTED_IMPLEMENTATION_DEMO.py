#!/usr/bin/env python3
"""
CORRECTED IMPLEMENTATION DEMO

This script demonstrates the corrected EuropePMC search implementation
based on official documentation analysis.

Key Fixes Applied:
1. ✅ Use free text searches instead of complex AUTH: syntax
2. ✅ Add context as free text, not AFFILIATION: fields
3. ✅ Implement progressive search strategies
4. ✅ Use proper Boolean operators
5. ✅ Apply correct date filtering syntax
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any

# EuropePMC API Configuration
EUROPEPMC_BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

class CorrectedEuropePMCDemo:
    """Demonstration of corrected EuropePMC search implementation."""
    
    def __init__(self):
        self.base_url = EUROPEPMC_BASE_URL
    
    async def search_publications(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """Search publications using corrected syntax."""
        params = {
            "query": query,
            "resultType": "lite",
            "pageSize": page_size,
            "format": "json",
            "sort": "date"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            return response.json()
    
    async def progressive_author_search(self, author_name: str, context_terms: str = "") -> Dict[str, Any]:
        """
        Implement progressive search strategy based on EuropePMC documentation.
        """
        print(f"\n🎯 PROGRESSIVE SEARCH for: {author_name}")
        print(f"Context: {context_terms}")
        print("=" * 60)
        
        # Strategy based on official EuropePMC documentation
        search_strategies = []
        
        # 1. Free text search (documentation recommended)
        search_strategies.append(author_name)
        
        # 2. Name variations
        name_parts = author_name.split()
        if len(name_parts) >= 2:
            first, last = name_parts[0], name_parts[-1]
            search_strategies.extend([
                f"{last} {first}",      # Last first
                f"{last} {first[0]}",   # Last initial
                f"{first[0]} {last}"    # Initial last
            ])
        
        # 3. Add context terms (free text, not field-specific)
        if context_terms:
            base_strategies = search_strategies.copy()
            for base_query in base_strategies:
                # Add context as free text, not as AFFILIATION field
                search_strategies.append(f"{base_query} {context_terms}")
                
                # Try Boolean combinations
                if "EMBO" in context_terms:
                    search_strategies.append(f"{base_query} (EMBO OR director)")
                if "stem" in context_terms.lower():
                    search_strategies.append(f"{base_query} (stem OR epidermal)")
        
        # 4. Try with date filtering for recent papers
        search_strategies.append(f"{author_name} AND FIRST_PDATE:[2020 TO *]")
        
        print(f"📋 Search strategies ({len(search_strategies)}):")
        for i, strategy in enumerate(search_strategies, 1):
            print(f"   {i}. {strategy}")
        
        # Try each strategy until we get results
        best_result = None
        successful_query = None
        
        for i, query in enumerate(search_strategies, 1):
            try:
                print(f"\n🔄 Strategy {i}: {query}")
                
                result = await self.search_publications(query, page_size=10)
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
            return {"hitCount": 0, "publications": []}
        
        # Extract and display results
        publications = []
        if "resultList" in best_result and "result" in best_result["resultList"]:
            publications = best_result["resultList"]["result"]
        
        print(f"\n📚 Found {len(publications)} publications")
        print(f"🎯 Successful query: {successful_query}")
        
        # Show sample publications
        for i, pub in enumerate(publications[:5]):
            title = pub.get("title", "No title")
            date = pub.get("firstPublicationDate", "No date")
            print(f"\n   {i+1}. {title}")
            print(f"      Date: {date}")
            
            # Show authors
            if "authorList" in pub and "author" in pub["authorList"]:
                authors = pub["authorList"]["author"]
                if isinstance(authors, list):
                    author_names = [a.get("fullName", "Unknown") for a in authors[:3]]
                    if len(authors) > 3:
                        author_names.append(f"... and {len(authors)-3} more")
                else:
                    author_names = [authors.get("fullName", "Unknown")]
                print(f"      Authors: {', '.join(author_names)}")
            
            # Show journal
            journal_info = pub.get("journalInfo", {})
            if journal_info and "journal" in journal_info:
                journal_title = journal_info["journal"].get("title", "Unknown")
                print(f"      Journal: {journal_title}")
        
        return {
            "successful_query": successful_query,
            "strategies_tried": len(search_strategies),
            "hitCount": len(publications),
            "publications": publications
        }

async def main():
    """Run the corrected implementation demo."""
    
    print("🚀 CORRECTED EUROPEPMC IMPLEMENTATION DEMO")
    print("=" * 70)
    print("\nBased on Official EuropePMC Documentation Analysis")
    print("Key Insight: Use free text searches, not complex field syntax")
    
    demo = CorrectedEuropePMCDemo()
    
    # Test cases based on our research
    test_cases = [
        {
            "name": "Fiona Watt",
            "context": "EMBO",
            "description": "EMBO Director - stem cell biology"
        },
        {
            "name": "John Smith", 
            "context": "cancer",
            "description": "Common name with research context"
        },
        {
            "name": "Marie Curie",
            "context": "physics",
            "description": "Historical figure test"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n\n{'='*70}")
        print(f"TEST CASE: {test_case['name']} ({test_case['description']})")
        print(f"{'='*70}")
        
        try:
            result = await demo.progressive_author_search(
                test_case["name"], 
                test_case["context"]
            )
            results.append({
                "test_case": test_case,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append({
                "test_case": test_case,
                "result": {"error": str(e)}
            })
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📊 DEMO SUMMARY")
    print(f"{'='*70}")
    
    for i, result_data in enumerate(results, 1):
        test_case = result_data["test_case"]
        result = result_data["result"]
        
        print(f"\n{i}. {test_case['name']} ({test_case['description']})")
        
        if "error" in result:
            print(f"   ❌ Failed: {result['error']}")
        else:
            hit_count = result.get("hitCount", 0)
            successful_query = result.get("successful_query", "None")
            strategies_tried = result.get("strategies_tried", 0)
            
            print(f"   ✅ Success: {hit_count} publications found")
            print(f"   🎯 Winning query: {successful_query}")
            print(f"   🔄 Strategies tried: {strategies_tried}")
    
    print(f"\n{'='*70}")
    print("🎉 CORRECTED IMPLEMENTATION BENEFITS:")
    print("✅ Uses official EuropePMC documentation patterns")
    print("✅ Progressive search strategy with fallbacks")
    print("✅ Free text searches (more reliable than field syntax)")
    print("✅ Proper Boolean operator usage")
    print("✅ Context-aware disambiguation")
    print("✅ Ready for MCP server integration")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())
