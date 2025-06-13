# EuropePMC MCP Server - Usage Examples

This document provides examples of how to use the EuropePMC MCP Server tools for biomedical literature search and analysis.

## Basic Search Examples

### 1. Simple Keyword Search
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "CRISPR gene editing",
    "page_size": 10
  }
}
```

### 2. Author-Specific Search
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "AUTH:\"Jennifer Doudna\"",
    "page_size": 20,
    "sort": "date"
  }
}
```

### 3. Journal-Specific Search
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "JOURNAL:\"Nature\" AND cancer",
    "page_size": 15,
    "result_type": "core"
  }
}
```

## Advanced Search Examples

### 1. Date Range Search
```json
{
  "tool": "advanced_search",
  "arguments": {
    "query": "machine learning",
    "filters": {
      "publication_date_from": "2020-01-01",
      "publication_date_to": "2023-12-31",
      "open_access_only": true
    },
    "page_size": 25
  }
}
```

### 2. Complex Query with Multiple Filters
```json
{
  "tool": "advanced_search",
  "arguments": {
    "query": "Alzheimer AND drug therapy",
    "filters": {
      "journal": "Nature Medicine",
      "has_full_text": true,
      "publication_date_from": "2022-01-01"
    },
    "sort": "cited",
    "page_size": 20
  }
}
```

## Author Disambiguation Examples

### 1. Search Publications by Author with Disambiguation
```json
{
  "tool": "search_author_publications",
  "arguments": {
    "author_name": "John Smith",
    "additional_terms": "cancer research",
    "disambiguation_threshold": 85,
    "page_size": 15
  }
}
```

### 2. High-Precision Author Search
```json
{
  "tool": "search_author_publications",
  "arguments": {
    "author_name": "Maria Garcia",
    "additional_terms": "AFFILIATION:\"Harvard Medical School\"",
    "disambiguation_threshold": 90,
    "page_size": 10
  }
}
```

## Publication Details and Analysis

### 1. Get Detailed Publication Information
```json
{
  "tool": "get_publication_details",
  "arguments": {
    "source": "MED",
    "identifier": "32205870",
    "data_type": "core"
  }
}
```

### 2. Get Citations for a Publication
```json
{
  "tool": "get_citations",
  "arguments": {
    "source": "MED",
    "identifier": "32205870",
    "page_size": 50
  }
}
```

### 3. Get References from a Publication
```json
{
  "tool": "get_references",
  "arguments": {
    "source": "PMC",
    "identifier": "7096066",
    "page_size": 30
  }
}
```

### 4. Get Database Cross-References
```json
{
  "tool": "get_database_links",
  "arguments": {
    "source": "MED",
    "identifier": "32205870"
  }
}
```

## Full-Text Access Examples

### 1. Get Full Text XML for Open Access Article
```json
{
  "tool": "get_full_text",
  "arguments": {
    "source": "PMC",
    "identifier": "7096066"
  }
}
```

## Complex Research Scenarios

### 1. COVID-19 Research Analysis
```json
{
  "tool": "advanced_search",
  "arguments": {
    "query": "COVID-19 OR SARS-CoV-2",
    "filters": {
      "publication_date_from": "2020-01-01",
      "open_access_only": true,
      "has_full_text": true
    },
    "sort": "cited",
    "page_size": 100
  }
}
```

### 2. Drug Discovery Research
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "MESH:\"Drug Discovery\" AND FIRST_PDATE:[2023-01-01 TO 2024-12-31]",
    "result_type": "core",
    "page_size": 50,
    "sort": "date"
  }
}
```

### 3. Biomarker Research in Cancer
```json
{
  "tool": "advanced_search",
  "arguments": {
    "query": "biomarker AND cancer",
    "filters": {
      "publication_date_from": "2022-01-01",
      "journal": "Nature",
      "has_full_text": true
    },
    "result_type": "core",
    "page_size": 25
  }
}
```

## Author Collaboration Analysis

### 1. Find Collaborations Between Authors
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "AUTH:\"Jennifer Doudna\" AND AUTH:\"Emmanuelle Charpentier\"",
    "result_type": "lite",
    "page_size": 20
  }
}
```

### 2. Institution-Based Research
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "AFFILIATION:\"MIT\" AND artificial intelligence",
    "page_size": 30,
    "sort": "cited"
  }
}
```

## Field-Specific Searches

### 1. Neuroscience Research
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "MESH:\"Neurosciences\" AND optogenetics",
    "result_type": "core",
    "page_size": 25,
    "sort": "date"
  }
}
```

### 2. Clinical Trials
```json
{
  "tool": "search_publications",
  "arguments": {
    "query": "MESH:\"Clinical Trials as Topic\" AND phase III",
    "page_size": 40,
    "sort": "date"
  }
}
```

## Tips for Effective Searching

### Query Syntax
- Use `AUTH:"Last First"` for author searches
- Use `JOURNAL:"Journal Name"` for journal-specific searches
- Use `MESH:"MeSH Term"` for Medical Subject Heading searches
- Use `FIRST_PDATE:[YYYY-MM-DD TO YYYY-MM-DD]` for date ranges
- Use `OPEN_ACCESS:Y` to limit to open access publications
- Use `HAS_FT:Y` to limit to publications with full text

### Boolean Operators
- `AND` - both terms must be present
- `OR` - either term can be present
- `NOT` - exclude the term
- Use parentheses for complex queries: `(cancer OR tumor) AND therapy`

### Wildcards
- Use `*` for wildcard matching: `cardi*` matches cardiology, cardiac, etc.

### Author Disambiguation Best Practices
- Use full names when possible for better disambiguation
- Include institutional affiliations in additional terms
- Adjust the threshold based on name commonality (higher for common names)
- Review the matching scores in the results

### Performance Optimization
- Use appropriate page sizes (25-100 for most cases)
- Use `lite` result type for overview searches
- Use `core` result type when you need full metadata
- Use `idlist` when you only need identifiers

## Error Handling

The server includes comprehensive error handling for:
- Invalid query syntax
- Network timeouts
- Rate limiting (automatic retry with backoff)
- Missing required parameters
- API service unavailability

All errors are returned with descriptive messages to help troubleshoot issues.
