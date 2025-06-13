#!/usr/bin/env python3
"""
CLI tool to test the EuropePMC MCP server interactively.
Usage: python test_mcp_cli.py [tool_name] [arguments...]

Examples:
  python test_mcp_cli.py search_publications "AUTH:\"Fiona Watt\" AND EMBO"
  python test_mcp_cli.py search_author_publications "Fiona Watt" --additional_terms "EMBO"
  python test_mcp_cli.py advanced_search "Fiona Watt" --date_from "2020-01-01"
"""

import asyncio
import json
import sys
import os
import argparse

# Add the src directory to the path so we can import the server modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from europepmc_server.server import EuropePMCServer

async def run_mcp_tool(tool_name, args_dict):
    """Run an MCP tool with the given arguments."""
    server = EuropePMCServer()
    
    # Initialize the client
    from europepmc_server.server import EuropePMCClient
    server.client = EuropePMCClient()
    
    try:
        if tool_name == "search_publications":
            result = await server._search_publications(args_dict)
        elif tool_name == "search_author_publications":
            result = await server._search_author_publications(args_dict)
        elif tool_name == "advanced_search":
            result = await server._advanced_search(args_dict)
        elif tool_name == "get_publication_details":
            result = await server._get_publication_details(args_dict)
        elif tool_name == "get_citations":
            result = await server._get_citations(args_dict)
        elif tool_name == "get_references":
            result = await server._get_references(args_dict)
        elif tool_name == "get_database_links":
            result = await server._get_database_links(args_dict)
        elif tool_name == "get_full_text":
            result = await server._get_full_text(args_dict)
        else:
            print(f"❌ Unknown tool: {tool_name}")
            return
        
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text
            try:
                # Try to parse as JSON for pretty printing
                data = json.loads(content)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                # If not JSON, print as is
                print(content)
        else:
            print("❌ No content returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to test EuropePMC MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for publications
  python test_mcp_cli.py search_publications "AUTH:\\"Fiona Watt\\" AND EMBO"
  
  # Search author publications with disambiguation
  python test_mcp_cli.py search_author_publications "Fiona Watt" --additional_terms "EMBO" --threshold 70
  
  # Advanced search with date filter
  python test_mcp_cli.py advanced_search "Fiona Watt" --date_from "2020-01-01" --date_to "2024-12-31"
  
  # Get publication details
  python test_mcp_cli.py get_publication_details "MED" "12345678"
  
  # List available tools
  python test_mcp_cli.py list_tools
        """
    )
    
    parser.add_argument('tool', help='MCP tool name')
    parser.add_argument('query', nargs='?', help='Search query or first argument')
    parser.add_argument('identifier', nargs='?', help='Publication identifier (for detail tools)')
    
    # Optional arguments for different tools
    parser.add_argument('--additional_terms', help='Additional search terms')
    parser.add_argument('--threshold', type=int, default=80, help='Disambiguation threshold (50-100)')
    parser.add_argument('--page_size', type=int, default=10, help='Number of results per page')
    parser.add_argument('--result_type', choices=['idlist', 'lite', 'core'], default='lite', help='Result type')
    parser.add_argument('--sort', choices=['relevance', 'date', 'cited'], help='Sort order')
    parser.add_argument('--date_from', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--date_to', help='End date (YYYY-MM-DD)')
    parser.add_argument('--journal', help='Journal name filter')
    parser.add_argument('--open_access_only', action='store_true', help='Limit to open access publications')
    parser.add_argument('--has_full_text', action='store_true', help='Limit to publications with full text')
    parser.add_argument('--exclude_corrections', action='store_true', help='Exclude corrections, corrigenda, and retractions (default: True)')
    parser.add_argument('--exclude_editorials', action='store_true', help='Exclude editorials and letters')
    parser.add_argument('--only_research_articles', action='store_true', help='Include only research articles (excludes reviews, editorials, etc.)')
    parser.add_argument('--include_preprints', action='store_true', help='Include preprints in results')
    parser.add_argument('--source_filter', nargs='+', choices=['MED', 'PMC', 'PPR', 'PAT', 'ETH', 'HIR', 'CTX', 'AGR', 'CBA', 'NBK'], help='Filter by data sources')
    
    args = parser.parse_args()
    
    if args.tool == "list_tools":
        print("📋 Available MCP Tools:")
        print("1. search_publications - General publication search")
        print("2. search_author_publications - Author-specific search with disambiguation")
        print("3. advanced_search - Search with filters (date, journal, etc.)")
        print("4. get_publication_details - Get detailed info for specific publications")
        print("5. get_citations - Get citing publications")
        print("6. get_references - Get referenced publications")
        print("7. get_database_links - Get cross-references")
        print("8. get_full_text - Get full text for open access articles")
        return
    
    # Build arguments dictionary based on tool
    args_dict = {}
    
    if args.tool == "search_publications":
        if not args.query:
            print("❌ Error: Query is required for search_publications")
            return
        args_dict = {
            "query": args.query,
            "result_type": args.result_type,
            "page_size": args.page_size
        }
        if args.sort:
            args_dict["sort"] = args.sort
    
    elif args.tool == "search_author_publications":
        if not args.query:
            print("❌ Error: Author name is required for search_author_publications")
            return
        args_dict = {
            "author_name": args.query,
            "page_size": args.page_size,
            "disambiguation_threshold": args.threshold
        }
        if args.additional_terms:
            args_dict["additional_terms"] = args.additional_terms
    
    elif args.tool == "advanced_search":
        if not args.query:
            print("❌ Error: Query is required for advanced_search")
            return
        args_dict = {
            "query": args.query,
            "result_type": args.result_type,
            "page_size": args.page_size
        }
        
        filters = {}
        if args.date_from:
            filters["publication_date_from"] = args.date_from
        if args.date_to:
            filters["publication_date_to"] = args.date_to
        if args.journal:
            filters["journal"] = args.journal
        if args.open_access_only:
            filters["open_access_only"] = True
        if args.has_full_text:
            filters["has_full_text"] = True
        
        if filters:
            args_dict["filters"] = filters
        
        if args.sort:
            args_dict["sort"] = args.sort
    
    elif args.tool in ["get_publication_details", "get_citations", "get_references", "get_database_links"]:
        if not args.query or not args.identifier:
            print(f"❌ Error: Both source and identifier are required for {args.tool}")
            print("Example: python test_mcp_cli.py get_publication_details MED 12345678")
            return
        args_dict = {
            "source": args.query,
            "identifier": args.identifier
        }
        if args.tool == "get_publication_details":
            args_dict["data_type"] = "core"
        elif args.tool in ["get_citations", "get_references"]:
            args_dict["page_size"] = args.page_size
    
    elif args.tool == "get_full_text":
        if not args.query or not args.identifier:
            print("❌ Error: Both source and identifier are required for get_full_text")
            print("Example: python test_mcp_cli.py get_full_text PMC 1234567")
            return
        args_dict = {
            "source": args.query,
            "identifier": args.identifier
        }
    
    else:
        print(f"❌ Unknown tool: {args.tool}")
        print("Use 'python test_mcp_cli.py list_tools' to see available tools")
        return
    
    print(f"🚀 Running MCP tool: {args.tool}")
    print(f"📋 Arguments: {json.dumps(args_dict, indent=2)}")
    print("=" * 60)
    
    asyncio.run(run_mcp_tool(args.tool, args_dict))

if __name__ == "__main__":
    main()
