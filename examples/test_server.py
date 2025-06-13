#!/usr/bin/env python3
"""
Simple test script for the EuropePMC MCP Server
"""

import asyncio
import json
from src.europepmc_server.server import EuropePMCServer

async def test_server():
    """Test the server functionality."""
    print("Testing EuropePMC MCP Server...")
    
    server = EuropePMCServer()
    
    # Test the client directly
    from src.europepmc_server.server import EuropePMCClient
    
    async with EuropePMCClient() as client:
        print("\n1. Testing basic search...")
        try:
            result = await client.search_publications(
                query="CRISPR",
                page_size=3
            )
            print(f"✓ Search successful! Found {result.get('hitCount', 0)} results")
            
            if "resultList" in result and "result" in result["resultList"]:
                first_result = result["resultList"]["result"][0]
                print(f"  First result: {first_result.get('title', 'No title')[:100]}...")
        except Exception as e:
            print(f"✗ Search failed: {e}")
        
        print("\n2. Testing publication details...")
        try:
            # Get details for a well-known paper
            result = await client.get_publication_details(
                source="MED",
                identifier="25326376"  # A CRISPR paper
            )
            print("✓ Publication details retrieved successfully!")
            if "result" in result:
                pub = result["result"]
                print(f"  Title: {pub.get('title', 'No title')[:100]}...")
        except Exception as e:
            print(f"✗ Publication details failed: {e}")
        
        print("\n3. Testing author disambiguation...")
        disambiguator = server.disambiguator
        
        # Test author matching
        target_author = "Jennifer A. Doudna"
        candidates = [
            "Doudna JA",
            "Jennifer Doudna", 
            "J. A. Doudna",
            "John Smith",
            "Doudna J"
        ]
        
        matches = disambiguator.match_authors(target_author, candidates, threshold=70)
        print(f"✓ Author disambiguation test:")
        for author, score in matches:
            print(f"  {author}: {score}%")
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_server())
