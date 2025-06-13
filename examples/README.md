# EuropePMC MCP Server Examples

This directory contains examples and test scripts for the EuropePMC MCP server.

## Main Examples

### 🚀 Advanced Search Example
**File:** `advanced_search_example.py`

Demonstrates the enhanced filtering capabilities including:
- Publication type filtering (exclude corrections, retractions, etc.)
- Enhanced time filtering with FIRST_PDATE
- Source filtering (MED, PMC, PPR, etc.)
- Open access and full text filtering

```bash
python examples/advanced_search_example.py
```

### 🛠️ CLI Tool
**File:** `test_mcp_cli.py`

Interactive command-line tool to test all MCP server functions.

```bash
# List available tools
python examples/test_mcp_cli.py list_tools

# Advanced search with filtering
python examples/test_mcp_cli.py advanced_search "stem cells" --date_from "2023-01-01" --open_access_only

# Author search with disambiguation
python examples/test_mcp_cli.py search_author_publications "Smith J" --additional_terms "cancer" --threshold 70
```

## Test Scripts

The following files contain various test scenarios and development examples:

- `test_enhanced_filtering.py` - Tests for enhanced filtering capabilities
- `test_mcp_server_working.py` - Comprehensive server functionality tests
- `demo_mcp_usage.py` - Basic usage demonstration
- `test_api_basic.py` - Basic API connectivity tests

## Development Files

Additional test files used during development are also included for reference.

## Usage

All examples can be run from the project root directory:

```bash
# Run the main advanced search example
python examples/advanced_search_example.py

# Use the CLI tool
python examples/test_mcp_cli.py [command] [options]
```

## Requirements

Make sure you have installed the project dependencies:

```bash
pip install -e .
```

Or install the required packages manually:

```bash
pip install httpx pydantic python-dateutil fuzzywuzzy python-levenshtein xmltodict asyncio-throttle
