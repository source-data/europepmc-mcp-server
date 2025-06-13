# EuropePMC MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the EuropePMC database for biomedical literature search and analysis, including advanced author disambiguation capabilities.

## Features

- **Comprehensive Search**: Search publications using the full EuropePMC query syntax
- **Enhanced Filtering**: Advanced publication type filtering (exclude corrections, retractions, etc.)
- **Time Filtering**: Precise date range filtering using FIRST_PDATE
- **Source Filtering**: Filter by data sources (PubMed, PMC, Preprints, etc.)
- **Author Disambiguation**: Advanced fuzzy matching algorithms to identify publications by specific authors
- **Citation Analysis**: Retrieve citations and references for publications
- **Full-Text Access**: Access full-text XML for open access publications
- **Database Cross-References**: Get links to related databases and resources
- **Rate Limiting**: Built-in rate limiting to respect API guidelines
- **Error Handling**: Robust error handling with retry mechanisms

## Installation

1. Clone or download this repository
2. Install the package and dependencies:

```bash
cd europepmc-server
pip install -e .
```

## Configuration

Add the server to your MCP settings configuration file:

### For Cline (VSCode Extension)

Edit `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "europepmc": {
      "command": "python",
      "args": ["/path/to/europepmc-server/src/europepmc_server/server.py"],
      "env": {}
    }
  }
}
```

### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "europepmc": {
      "command": "python",
      "args": ["/path/to/europepmc-server/src/europepmc_server/server.py"],
      "env": {}
    }
  }
}
```

## Available Tools

### 1. search_publications
Search for publications in the EuropePMC database.

**Parameters:**
- `query` (required): Search query with support for field-specific searches
- `result_type`: Type of results ("idlist", "lite", "core")
- `page_size`: Number of results per page (1-1000)
- `sort`: Sort order ("relevance", "date", "cited")
- `synonym`: Include synonym expansion (boolean)

**Example queries:**
- `"CRISPR gene editing"`
- `"AUTH:\"Smith J\" AND JOURNAL:\"Nature\""`
- `"cancer AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]"`

### 2. get_publication_details
Get detailed information about a specific publication.

**Parameters:**
- `source` (required): Source database ("MED", "PMC", "PAT", "ETH", "HIR", "CTX")
- `identifier` (required): Publication identifier (PMID, PMCID, etc.)
- `data_type`: Level of detail ("core", "lite")

### 3. get_citations
Get publications that cite a specific publication.

**Parameters:**
- `source` (required): Source database
- `identifier` (required): Publication identifier
- `page_size`: Number of results per page

### 4. get_references
Get publications referenced by a specific publication.

**Parameters:**
- `source` (required): Source database
- `identifier` (required): Publication identifier
- `page_size`: Number of results per page

### 5. search_author_publications
Search for publications by a specific author with disambiguation.

**Parameters:**
- `author_name` (required): Author name to search for
- `additional_terms`: Additional search terms to refine results
- `page_size`: Number of results per page
- `disambiguation_threshold`: Minimum similarity score for author matching (50-100)

### 6. get_database_links
Get cross-references to other databases for a publication.

**Parameters:**
- `source` (required): Source database
- `identifier` (required): Publication identifier

### 7. get_full_text
Get full text XML for open access publications.

**Parameters:**
- `source` (required): Source database (only "PMC" supported)
- `identifier` (required): PMC identifier

### 8. advanced_search
Perform advanced search with complex queries and filters.

**Parameters:**
- `query` (required): Advanced search query
- `filters`: Object with optional filters:
  - `publication_date_from`: Start date (YYYY-MM-DD)
  - `publication_date_to`: End date (YYYY-MM-DD)
  - `journal`: Journal name filter
  - `open_access_only`: Limit to open access publications
  - `has_full_text`: Limit to publications with full text
- `result_type`: Type of results to return
- `page_size`: Number of results per page
- `sort`: Sort order for results

## Author Disambiguation

The server includes sophisticated author disambiguation using fuzzy string matching:

- **Name Normalization**: Removes common suffixes and normalizes spacing
- **Initial Matching**: Bonus scoring for matching initials
- **Multiple Algorithms**: Uses ratio, partial ratio, token sort, and token set matching
- **Configurable Threshold**: Adjustable similarity threshold (50-100)
- **Ranking**: Results ranked by best match score

## API Rate Limiting

The server implements conservative rate limiting:
- 10 requests per second
- Burst capacity of 20 requests
- Automatic retry with exponential backoff
- Respect for HTTP 429 (rate limit) responses

## Error Handling

- Comprehensive error handling for network issues
- Automatic retry for transient failures
- Detailed error messages for debugging
- Graceful handling of API response variations

## Examples and Testing

### Quick Start Example

Run the advanced search example to see the enhanced filtering capabilities:

```bash
python examples/advanced_search_example.py
```

This demonstrates:
- Publication type filtering (exclude corrections, retractions)
- Enhanced time filtering with FIRST_PDATE
- Source filtering (MED, PMC, PPR, etc.)
- Open access and full text filtering
- Combined filtering for precise results

### CLI Testing Tool

Use the interactive CLI tool to test all server functions:

```bash
# List available tools
python examples/test_mcp_cli.py list_tools

# Advanced search with filtering
python examples/test_mcp_cli.py advanced_search "stem cells" --date_from "2023-01-01" --open_access_only

# Author search with disambiguation
python examples/test_mcp_cli.py search_author_publications "Smith J" --additional_terms "cancer" --threshold 70
```

See `examples/README.md` for more detailed examples and usage instructions.

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

### Type Checking

```bash
mypy src/
```

## EuropePMC Query Syntax

The server supports the full EuropePMC query syntax:

### Field Codes
- `AUTH`: Author
- `JOURNAL`: Journal name
- `TITLE`: Article title
- `ABSTRACT`: Abstract text
- `MESH`: MeSH terms
- `FIRST_PDATE`: First publication date
- `OPEN_ACCESS`: Open access status (Y/N)
- `HAS_FT`: Has full text (Y/N)

### Operators
- `AND`, `OR`, `NOT`: Boolean operators
- `"phrase"`: Exact phrase matching
- `[date1 TO date2]`: Date range
- `*`: Wildcard

### Examples
```
AUTH:"Smith J" AND JOURNAL:"Nature"
cancer AND FIRST_PDATE:[2020-01-01 TO 2023-12-31]
"machine learning" AND OPEN_ACCESS:Y
MESH:"Alzheimer Disease" AND HAS_FT:Y
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the EuropePMC API documentation: https://europepmc.org/developers
- Review the MCP specification: https://modelcontextprotocol.io/
- Open an issue in this repository
