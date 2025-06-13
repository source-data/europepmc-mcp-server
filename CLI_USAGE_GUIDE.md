# EuropePMC MCP Server CLI Usage Guide

## Quick Start

You can test the EuropePMC MCP server using the provided CLI tool:

```bash
python examples/test_mcp_cli.py [tool_name] [arguments...]
```

## Available Tools

List all available tools:
```bash
python examples/test_mcp_cli.py list_tools
```

## Example Commands for Your Search (Fiona M Watt + EMBO)

### 1. Basic Publication Search
```bash
# Search for publications with EMBO connection
python examples/test_mcp_cli.py search_publications "AUTH:\"Smith J\" AND cancer" --page_size 5

# Alternative search formats
python examples/test_mcp_cli.py search_publications "AUTH:\"Johnson A\" AND diabetes"
python examples/test_mcp_cli.py search_publications "stem cells AND regeneration"
```

### 2. Author-Specific Search with Disambiguation
```bash
# Search with author disambiguation (recommended for precise results)
python examples/test_mcp_cli.py search_author_publications "Smith J" --additional_terms "cancer" --threshold 70

# Adjust threshold for more/fewer results (50-100)
python examples/test_mcp_cli.py search_author_publications "Johnson A" --additional_terms "diabetes" --threshold 60
```

### 3. Advanced Search with Enhanced Filters
```bash
# Search with date filters (NEW: Enhanced time filtering)
python examples/test_mcp_cli.py advanced_search "CRISPR gene editing" --date_from "2020-01-01" --date_to "2024-12-31"

# Exclude corrections and retractions (NEW: Publication type filtering)
python examples/test_mcp_cli.py advanced_search "stem cells" --exclude_corrections --exclude_editorials

# Open access only with full text
python examples/test_mcp_cli.py advanced_search "machine learning healthcare" --open_access_only --has_full_text

# Filter by data sources (NEW: Source filtering)
python examples/test_mcp_cli.py advanced_search "COVID-19 vaccine" --source_filter MED PMC

# Research articles only (excludes reviews, editorials, etc.)
python examples/test_mcp_cli.py advanced_search "artificial intelligence" --only_research_articles

# Include preprints in results
python examples/test_mcp_cli.py advanced_search "climate change" --include_preprints
```

### 4. Get Publication Details
```bash
# Get detailed information for a specific publication (use PMID from search results)
python examples/test_mcp_cli.py get_publication_details "MED" "40360736"
```

### 5. Citation Analysis
```bash
# Get publications that cite a specific paper
python examples/test_mcp_cli.py get_citations "MED" "40360736" --page_size 10

# Get references from a specific paper
python examples/test_mcp_cli.py get_references "MED" "40360736"
```

### 6. Full Text Access
```bash
# Get full text for open access PMC articles
python examples/test_mcp_cli.py get_full_text "PMC" "12152184"
```

## Command Options

### Common Options
- `--page_size N` - Number of results to return (default: 10)
- `--result_type TYPE` - Result detail level: `idlist`, `lite`, `core` (default: lite)
- `--sort ORDER` - Sort by: `relevance`, `date`, `cited`

### Search-Specific Options
- `--additional_terms "TERMS"` - Additional search terms
- `--threshold N` - Disambiguation threshold 50-100 (default: 80)

### Advanced Search Filters
- `--date_from "YYYY-MM-DD"` - Start date filter
- `--date_to "YYYY-MM-DD"` - End date filter
- `--journal "JOURNAL_NAME"` - Filter by journal
- `--open_access_only` - Limit to open access publications
- `--has_full_text` - Limit to publications with full text

## Example Output

When you run a search, you'll get JSON output like this:

```json
{
  "hit_count": 31,
  "publications": [
    {
      "id": "40360736",
      "pmid": "40360736",
      "pmcid": "PMC12152184",
      "doi": "10.1038/s44319-025-00468-8",
      "title": "Controlled anarchy.",
      "publication_date": "2025-05-13",
      "is_open_access": true,
      "has_pdf": true
    }
  ]
}
```

## Test Results for Your Search

✅ **Working Commands Tested:**

1. **Basic Search:** Found 31 publications for `AUTH:"Fiona Watt" AND EMBO`
2. **API Connectivity:** Successfully connected to EuropePMC
3. **JSON Output:** Properly formatted results returned
4. **Filtering:** Page size and other filters working correctly

## Troubleshooting

If you encounter issues:

1. **Import Errors:** Make sure you're running from the project root directory
2. **Network Issues:** Check your internet connection
3. **No Results:** Try different name variations or lower disambiguation thresholds
4. **Rate Limiting:** The tool automatically handles rate limits with retries

## Integration with MCP Applications

Once you've tested the CLI and confirmed it works for your needs, you can integrate the MCP server with applications like:

- **Cline (VSCode Extension)**
- **Claude Desktop**
- **Other MCP-compatible tools**

The server provides the same functionality through the standard MCP protocol.
