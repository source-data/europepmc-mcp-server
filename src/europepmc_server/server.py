#!/usr/bin/env python3
"""
EuropePMC MCP Server

A Model Context Protocol server that provides tools for querying the EuropePMC database,
including comprehensive search capabilities, author disambiguation, and metadata retrieval.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, urlencode

import httpx
import xmltodict
from asyncio_throttle import Throttler
from fuzzywuzzy import fuzz, process
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EuropePMC API Configuration
EUROPEPMC_BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUROPEPMC_TEST_URL = "https://www.ebi.ac.uk/europepmc/webservices/test/rest"

# Rate limiting: EuropePMC allows reasonable request rates
# We'll implement conservative rate limiting to be respectful
RATE_LIMIT_REQUESTS_PER_SECOND = 10
RATE_LIMIT_BURST = 20

# Request timeout settings
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 3


class EuropePMCError(Exception):
    """Custom exception for EuropePMC API errors."""
    pass


class AuthorInfo(BaseModel):
    """Model for author information."""
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    initials: Optional[str] = None
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class PublicationInfo(BaseModel):
    """Model for publication information."""
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: List[AuthorInfo] = Field(default_factory=list)
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    mesh_terms: List[str] = Field(default_factory=list)
    citation_count: Optional[int] = None
    is_open_access: bool = False


class EuropePMCClient:
    """Client for interacting with the EuropePMC API."""
    
    def __init__(self, use_test_api: bool = False):
        self.base_url = EUROPEPMC_TEST_URL if use_test_api else EUROPEPMC_BASE_URL
        self.throttler = Throttler(rate_limit=RATE_LIMIT_REQUESTS_PER_SECOND, period=1.0)
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(REQUEST_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a rate-limited request to the EuropePMC API."""
        async with self.throttler:
            url = f"{self.base_url}/{endpoint}"
            
            for attempt in range(MAX_RETRIES):
                try:
                    if method.upper() == "POST":
                        response = await self.client.post(url, params=params, json=data)
                    else:
                        response = await self.client.get(url, params=params)
                    
                    response.raise_for_status()
                    
                    # Handle different response formats
                    content_type = response.headers.get("content-type", "").lower()
                    
                    if "application/json" in content_type:
                        return response.json()
                    elif "application/xml" in content_type or "text/xml" in content_type:
                        # Convert XML to dict
                        xml_content = response.text
                        return xmltodict.parse(xml_content)
                    else:
                        # Return raw text for other formats
                        return {"content": response.text, "content_type": content_type}
                
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    elif e.response.status_code >= 500:  # Server error
                        if attempt < MAX_RETRIES - 1:
                            wait_time = 2 ** attempt
                            logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                    raise EuropePMCError(error_msg)
                
                except httpx.RequestError as e:
                    if attempt < MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request error: {e}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    raise EuropePMCError(f"Request failed: {e}")
            
            raise EuropePMCError(f"Failed after {MAX_RETRIES} attempts")
    
    async def search_publications(
        self,
        query: str,
        result_type: str = "lite",
        page_size: int = 25,
        cursor_mark: Optional[str] = None,
        sort: Optional[str] = None,
        synonym: bool = True,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Search for publications using the EuropePMC search API."""
        params = {
            "query": query,
            "resultType": result_type,
            "pageSize": min(page_size, 1000),  # API limit
            "format": format,
            "synonym": "true" if synonym else "false"
        }
        
        if cursor_mark:
            params["cursorMark"] = cursor_mark
        
        if sort:
            params["sort"] = sort
        
        return await self._make_request("search", params)
    
    async def get_publication_details(
        self,
        source: str,
        identifier: str,
        data_type: str = "core",
        format: str = "json"
    ) -> Dict[str, Any]:
        """Get detailed information about a specific publication."""
        endpoint = f"{source}/{identifier}"
        params = {
            "format": format
        }
        
        if data_type != "core":
            endpoint += f"/{data_type}"
        
        return await self._make_request(endpoint, params)
    
    async def get_citations(
        self,
        source: str,
        identifier: str,
        page_size: int = 25,
        cursor_mark: Optional[str] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Get citations for a specific publication."""
        endpoint = f"{source}/{identifier}/citations"
        params = {
            "pageSize": min(page_size, 1000),
            "format": format
        }
        
        if cursor_mark:
            params["cursorMark"] = cursor_mark
        
        return await self._make_request(endpoint, params)
    
    async def get_references(
        self,
        source: str,
        identifier: str,
        page_size: int = 25,
        cursor_mark: Optional[str] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Get references for a specific publication."""
        endpoint = f"{source}/{identifier}/references"
        params = {
            "pageSize": min(page_size, 1000),
            "format": format
        }
        
        if cursor_mark:
            params["cursorMark"] = cursor_mark
        
        return await self._make_request(endpoint, params)
    
    async def get_database_links(
        self,
        source: str,
        identifier: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Get database cross-references for a publication."""
        endpoint = f"{source}/{identifier}/databaseLinks"
        params = {"format": format}
        
        return await self._make_request(endpoint, params)
    
    async def get_full_text_xml(
        self,
        source: str,
        identifier: str
    ) -> Dict[str, Any]:
        """Get full text XML for open access publications."""
        endpoint = f"{source}/{identifier}/fullTextXML"
        return await self._make_request(endpoint)
    
    async def get_supplementary_files(
        self,
        source: str,
        identifier: str
    ) -> Dict[str, Any]:
        """Get supplementary files for a publication."""
        endpoint = f"{source}/{identifier}/supplementaryFiles"
        return await self._make_request(endpoint)


class AuthorDisambiguator:
    """Utility class for author disambiguation using fuzzy matching."""
    
    @staticmethod
    def normalize_author_name(name: str) -> str:
        """Normalize author name for comparison."""
        # Remove extra whitespace, convert to lowercase
        normalized = " ".join(name.strip().lower().split())
        # Remove common suffixes and prefixes
        suffixes = ["jr", "sr", "ii", "iii", "iv", "phd", "md", "dr"]
        words = normalized.split()
        filtered_words = [w for w in words if w not in suffixes]
        return " ".join(filtered_words)
    
    @staticmethod
    def extract_initials(name: str) -> str:
        """Extract initials from a name."""
        words = name.strip().split()
        initials = []
        for word in words:
            if word and word[0].isalpha():
                initials.append(word[0].upper())
        return "".join(initials)
    
    @classmethod
    def match_authors(
        cls,
        target_author: str,
        candidate_authors: List[str],
        threshold: int = 80
    ) -> List[tuple]:
        """
        Match a target author against a list of candidate authors.
        Returns list of (author, score) tuples above threshold.
        """
        normalized_target = cls.normalize_author_name(target_author)
        target_initials = cls.extract_initials(target_author)
        
        matches = []
        
        for candidate in candidate_authors:
            normalized_candidate = cls.normalize_author_name(candidate)
            candidate_initials = cls.extract_initials(candidate)
            
            # Calculate various similarity scores
            full_name_score = fuzz.ratio(normalized_target, normalized_candidate)
            partial_score = fuzz.partial_ratio(normalized_target, normalized_candidate)
            token_sort_score = fuzz.token_sort_ratio(normalized_target, normalized_candidate)
            token_set_score = fuzz.token_set_ratio(normalized_target, normalized_candidate)
            
            # Bonus for matching initials
            initials_bonus = 10 if target_initials == candidate_initials else 0
            
            # Calculate weighted average score
            final_score = max(
                full_name_score,
                partial_score,
                token_sort_score,
                token_set_score
            ) + initials_bonus
            
            if final_score >= threshold:
                matches.append((candidate, min(final_score, 100)))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    @classmethod
    def disambiguate_author_publications(
        cls,
        author_name: str,
        publications: List[Dict[str, Any]],
        threshold: int = 80
    ) -> List[Dict[str, Any]]:
        """
        Filter publications to those likely authored by the target author.
        """
        disambiguated = []
        
        for pub in publications:
            # Extract author names from publication
            pub_authors = []
            
            # Handle different response formats
            if "authorList" in pub and "author" in pub["authorList"]:
                authors_data = pub["authorList"]["author"]
                if isinstance(authors_data, list):
                    for author in authors_data:
                        if isinstance(author, dict) and "fullName" in author:
                            pub_authors.append(author["fullName"])
                elif isinstance(authors_data, dict) and "fullName" in authors_data:
                    pub_authors.append(authors_data["fullName"])
            
            # Try alternative author field structures
            if not pub_authors and "authors" in pub:
                if isinstance(pub["authors"], list):
                    pub_authors = [str(author) for author in pub["authors"]]
                elif isinstance(pub["authors"], str):
                    pub_authors = [pub["authors"]]
            
            # Perform author matching
            if pub_authors:
                matches = cls.match_authors(author_name, pub_authors, threshold)
                if matches:
                    # Add matching information to publication
                    pub_copy = pub.copy()
                    pub_copy["author_matches"] = matches
                    pub_copy["best_match_score"] = matches[0][1]
                    disambiguated.append(pub_copy)
        
        # Sort by best match score
        disambiguated.sort(key=lambda x: x.get("best_match_score", 0), reverse=True)
        return disambiguated


class EuropePMCServer:
    """Main MCP server class for EuropePMC functionality."""
    
    def __init__(self):
        self.server = Server("europepmc-server")
        self.client: Optional[EuropePMCClient] = None
        self.disambiguator = AuthorDisambiguator()
        
        # Register tool handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="search_publications",
                        description="Search for publications in the EuropePMC database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query (supports field-specific searches like 'AUTH:\"Smith J\" AND JOURNAL:\"Nature\"')"
                                },
                                "result_type": {
                                    "type": "string",
                                    "enum": ["idlist", "lite", "core"],
                                    "default": "lite",
                                    "description": "Type of results to return (idlist: IDs only, lite: key metadata, core: full metadata)"
                                },
                                "page_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 1000,
                                    "default": 25,
                                    "description": "Number of results per page"
                                },
                                "sort": {
                                    "type": "string",
                                    "enum": ["relevance", "date", "cited"],
                                    "description": "Sort order for results"
                                },
                                "synonym": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Include synonym expansion in search"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="get_publication_details",
                        description="Get detailed information about a specific publication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["MED", "PMC", "PAT", "ETH", "HIR", "CTX"],
                                    "description": "Source database (MED=PubMed, PMC=PMC, etc.)"
                                },
                                "identifier": {
                                    "type": "string",
                                    "description": "Publication identifier (PMID, PMCID, etc.)"
                                },
                                "data_type": {
                                    "type": "string",
                                    "enum": ["core", "lite"],
                                    "default": "core",
                                    "description": "Level of detail to retrieve"
                                }
                            },
                            "required": ["source", "identifier"]
                        }
                    ),
                    Tool(
                        name="get_citations",
                        description="Get publications that cite a specific publication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["MED", "PMC", "PAT", "ETH", "HIR", "CTX"],
                                    "description": "Source database"
                                },
                                "identifier": {
                                    "type": "string",
                                    "description": "Publication identifier"
                                },
                                "page_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 1000,
                                    "default": 25,
                                    "description": "Number of results per page"
                                }
                            },
                            "required": ["source", "identifier"]
                        }
                    ),
                    Tool(
                        name="get_references",
                        description="Get publications referenced by a specific publication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["MED", "PMC", "PAT", "ETH", "HIR", "CTX"],
                                    "description": "Source database"
                                },
                                "identifier": {
                                    "type": "string",
                                    "description": "Publication identifier"
                                },
                                "page_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 1000,
                                    "default": 25,
                                    "description": "Number of results per page"
                                }
                            },
                            "required": ["source", "identifier"]
                        }
                    ),
                    Tool(
                        name="search_author_publications",
                        description="Search for publications by a specific author with disambiguation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "author_name": {
                                    "type": "string",
                                    "description": "Author name to search for"
                                },
                                "additional_terms": {
                                    "type": "string",
                                    "description": "Additional search terms to refine results (e.g., institution, keywords)"
                                },
                                "page_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 1000,
                                    "default": 25,
                                    "description": "Number of results per page"
                                },
                                "disambiguation_threshold": {
                                    "type": "integer",
                                    "minimum": 50,
                                    "maximum": 100,
                                    "default": 80,
                                    "description": "Minimum similarity score for author matching (50-100)"
                                }
                            },
                            "required": ["author_name"]
                        }
                    ),
                    Tool(
                        name="get_database_links",
                        description="Get cross-references to other databases for a publication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["MED", "PMC", "PAT", "ETH", "HIR", "CTX"],
                                    "description": "Source database"
                                },
                                "identifier": {
                                    "type": "string",
                                    "description": "Publication identifier"
                                }
                            },
                            "required": ["source", "identifier"]
                        }
                    ),
                    Tool(
                        name="get_full_text",
                        description="Get full text XML for open access publications",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["PMC"],
                                    "description": "Source database (only PMC supported for full text)"
                                },
                                "identifier": {
                                    "type": "string",
                                    "description": "PMC identifier (without PMC prefix)"
                                }
                            },
                            "required": ["source", "identifier"]
                        }
                    ),
                    Tool(
                        name="advanced_search",
                        description="Perform advanced search with complex queries and filters",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Advanced search query with field codes"
                                },
                                "filters": {
                                    "type": "object",
                                    "properties": {
                                        "publication_date_from": {
                                            "type": "string",
                                            "description": "Start date (YYYY-MM-DD format)"
                                        },
                                        "publication_date_to": {
                                            "type": "string",
                                            "description": "End date (YYYY-MM-DD format)"
                                        },
                                        "journal": {
                                            "type": "string",
                                            "description": "Journal name filter"
                                        },
                                        "open_access_only": {
                                            "type": "boolean",
                                            "description": "Limit to open access publications"
                                        },
                                        "has_full_text": {
                                            "type": "boolean",
                                            "description": "Limit to publications with full text available"
                                        }
                                    }
                                },
                                "result_type": {
                                    "type": "string",
                                    "enum": ["idlist", "lite", "core"],
                                    "default": "lite",
                                    "description": "Type of results to return"
                                },
                                "page_size": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 1000,
                                    "default": 25,
                                    "description": "Number of results per page"
                                },
                                "sort": {
                                    "type": "string",
                                    "enum": ["relevance", "date", "cited"],
                                    "description": "Sort order for results"
                                }
                            },
                            "required": ["query"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls."""
            try:
                if not self.client:
                    self.client = EuropePMCClient()
                
                if request.name == "search_publications":
                    return await self._search_publications(request.arguments or {})
                elif request.name == "get_publication_details":
                    return await self._get_publication_details(request.arguments or {})
                elif request.name == "get_citations":
                    return await self._get_citations(request.arguments or {})
                elif request.name == "get_references":
                    return await self._get_references(request.arguments or {})
                elif request.name == "search_author_publications":
                    return await self._search_author_publications(request.arguments or {})
                elif request.name == "get_database_links":
                    return await self._get_database_links(request.arguments or {})
                elif request.name == "get_full_text":
                    return await self._get_full_text(request.arguments or {})
                elif request.name == "advanced_search":
                    return await self._advanced_search(request.arguments or {})
                else:
                    raise ValueError(f"Unknown tool: {request.name}")
            
            except Exception as e:
                logger.error(f"Error handling tool call {request.name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _search_publications(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle publication search requests."""
        query = args.get("query", "")
        result_type = args.get("result_type", "lite")
        page_size = args.get("page_size", 25)
        sort = args.get("sort")
        synonym = args.get("synonym", True)
        
        if not query:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Query parameter is required")],
                isError=True
            )
        
        try:
            result = await self.client.search_publications(
                query=query,
                result_type=result_type,
                page_size=page_size,
                sort=sort,
                synonym=synonym
            )
            
            # Format the response
            formatted_result = self._format_search_results(result)
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(formatted_result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Search failed: {str(e)}")],
                isError=True
            )
    
    async def _get_publication_details(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle publication details requests."""
        source = args.get("source", "")
        identifier = args.get("identifier", "")
        data_type = args.get("data_type", "core")
        
        if not source or not identifier:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Source and identifier are required")],
                isError=True
            )
        
        try:
            result = await self.client.get_publication_details(
                source=source,
                identifier=identifier,
                data_type=data_type
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get publication details: {str(e)}")],
                isError=True
            )
    
    async def _get_citations(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle citation requests."""
        source = args.get("source", "")
        identifier = args.get("identifier", "")
        page_size = args.get("page_size", 25)
        
        if not source or not identifier:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Source and identifier are required")],
                isError=True
            )
        
        try:
            result = await self.client.get_citations(
                source=source,
                identifier=identifier,
                page_size=page_size
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get citations: {str(e)}")],
                isError=True
            )
    
    async def _get_references(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle reference requests."""
        source = args.get("source", "")
        identifier = args.get("identifier", "")
        page_size = args.get("page_size", 25)
        
        if not source or not identifier:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Source and identifier are required")],
                isError=True
            )
        
        try:
            result = await self.client.get_references(
                source=source,
                identifier=identifier,
                page_size=page_size
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get references: {str(e)}")],
                isError=True
            )
    
    async def _search_author_publications(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle author publication search with disambiguation."""
        author_name = args.get("author_name", "")
        additional_terms = args.get("additional_terms", "")
        page_size = args.get("page_size", 25)
        threshold = args.get("disambiguation_threshold", 90)
        
        if not author_name:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Author name is required")],
                isError=True
            )
        
        try:
            # Build search query
            query_parts = [f'AUTH:"{author_name}"']
            if additional_terms:
                query_parts.append(additional_terms)
            
            query = " AND ".join(query_parts)
            
            # Search for publications
            result = await self.client.search_publications(
                query=query,
                result_type="lite",
                page_size=page_size * 2  # Get more results for disambiguation
            )
            
            # Extract publications from result
            publications = []
            if "resultList" in result and "result" in result["resultList"]:
                publications = result["resultList"]["result"]
            
            # Perform author disambiguation
            disambiguated_pubs = self.disambiguator.disambiguate_author_publications(
                author_name, publications, threshold
            )
            
            # Limit to requested page size
            disambiguated_pubs = disambiguated_pubs[:page_size]
            
            # Format response
            formatted_result = {
                "query": query,
                "author_searched": author_name,
                "disambiguation_threshold": threshold,
                "total_found": len(publications),
                "after_disambiguation": len(disambiguated_pubs),
                "publications": disambiguated_pubs
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(formatted_result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Author search failed: {str(e)}")],
                isError=True
            )
    
    async def _get_database_links(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle database links requests."""
        source = args.get("source", "")
        identifier = args.get("identifier", "")
        
        if not source or not identifier:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Source and identifier are required")],
                isError=True
            )
        
        try:
            result = await self.client.get_database_links(
                source=source,
                identifier=identifier
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get database links: {str(e)}")],
                isError=True
            )
    
    async def _get_full_text(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle full text requests."""
        source = args.get("source", "")
        identifier = args.get("identifier", "")
        
        if not source or not identifier:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Source and identifier are required")],
                isError=True
            )
        
        if source != "PMC":
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Full text is only available for PMC articles")],
                isError=True
            )
        
        try:
            result = await self.client.get_full_text_xml(
                source=source,
                identifier=identifier
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get full text: {str(e)}")],
                isError=True
            )
    
    async def _advanced_search(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle advanced search requests."""
        query = args.get("query", "")
        filters = args.get("filters", {})
        result_type = args.get("result_type", "lite")
        page_size = args.get("page_size", 25)
        sort = args.get("sort")
        
        if not query:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Query parameter is required")],
                isError=True
            )
        
        try:
            # Build advanced query with filters
            query_parts = [query]
            
            # Add date filters
            if filters.get("publication_date_from"):
                query_parts.append(f'FIRST_PDATE:[{filters["publication_date_from"]} TO *]')
            
            if filters.get("publication_date_to"):
                query_parts.append(f'FIRST_PDATE:[* TO {filters["publication_date_to"]}]')
            
            # Add journal filter
            if filters.get("journal"):
                query_parts.append(f'JOURNAL:"{filters["journal"]}"')
            
            # Add open access filter
            if filters.get("open_access_only"):
                query_parts.append("OPEN_ACCESS:Y")
            
            # Add full text filter
            if filters.get("has_full_text"):
                query_parts.append("HAS_FT:Y")
            
            final_query = " AND ".join(query_parts)
            
            # Perform search
            result = await self.client.search_publications(
                query=final_query,
                result_type=result_type,
                page_size=page_size,
                sort=sort
            )
            
            # Format the response
            formatted_result = self._format_search_results(result)
            formatted_result["original_query"] = query
            formatted_result["applied_filters"] = filters
            formatted_result["final_query"] = final_query
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(formatted_result, indent=2))]
            )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Advanced search failed: {str(e)}")],
                isError=True
            )
    
    def _format_search_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format search results for better readability."""
        formatted = {
            "hit_count": result.get("hitCount", 0),
            "next_cursor_mark": result.get("nextCursorMark"),
            "request": result.get("request", {}),
            "publications": []
        }
        
        if "resultList" in result and "result" in result["resultList"]:
            publications = result["resultList"]["result"]
            
            for pub in publications:
                formatted_pub = {
                    "id": pub.get("id"),
                    "source": pub.get("source"),
                    "pmid": pub.get("pmid"),
                    "pmcid": pub.get("pmcid"),
                    "doi": pub.get("doi"),
                    "title": pub.get("title"),
                    "authors": self._extract_authors(pub),
                    "journal": self._extract_journal_info(pub),
                    "publication_date": pub.get("firstPublicationDate") or pub.get("pubDate"),
                    "abstract": pub.get("abstractText"),
                    "keywords": pub.get("keywordList", {}).get("keyword", []) if pub.get("keywordList") else [],
                    "mesh_terms": self._extract_mesh_terms(pub),
                    "citation_count": pub.get("citedByCount"),
                    "is_open_access": pub.get("isOpenAccess") == "Y",
                    "has_pdf": pub.get("hasPDF") == "Y",
                    "has_full_text": pub.get("hasTextMinedTerms") == "Y"
                }
                
                # Add author matching info if present
                if "author_matches" in pub:
                    formatted_pub["author_matches"] = pub["author_matches"]
                    formatted_pub["best_match_score"] = pub["best_match_score"]
                
                formatted["publications"].append(formatted_pub)
        
        return formatted
    
    def _extract_authors(self, publication: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract author information from publication data."""
        authors = []
        
        if "authorList" in publication and "author" in publication["authorList"]:
            author_data = publication["authorList"]["author"]
            
            # Handle both single author and list of authors
            if isinstance(author_data, dict):
                author_data = [author_data]
            
            for author in author_data:
                if isinstance(author, dict):
                    author_info = {
                        "full_name": author.get("fullName", ""),
                        "first_name": author.get("firstName", ""),
                        "last_name": author.get("lastName", ""),
                        "initials": author.get("initials", ""),
                        "affiliation": author.get("affiliation", ""),
                        "orcid": author.get("authorId", {}).get("value") if author.get("authorId") else None
                    }
                    authors.append(author_info)
        
        return authors
    
    def _extract_journal_info(self, publication: Dict[str, Any]) -> Dict[str, Any]:
        """Extract journal information from publication data."""
        journal_info = {
            "title": publication.get("journalInfo", {}).get("journal", {}).get("title", ""),
            "issn": publication.get("journalInfo", {}).get("journal", {}).get("issn", ""),
            "volume": publication.get("journalInfo", {}).get("volume", ""),
            "issue": publication.get("journalInfo", {}).get("issue", ""),
            "pages": publication.get("pageInfo", "")
        }
        
        return journal_info
    
    def _extract_mesh_terms(self, publication: Dict[str, Any]) -> List[str]:
        """Extract MeSH terms from publication data."""
        mesh_terms = []
        
        if "meshHeadingList" in publication and "meshHeading" in publication["meshHeadingList"]:
            mesh_data = publication["meshHeadingList"]["meshHeading"]
            
            # Handle both single term and list of terms
            if isinstance(mesh_data, dict):
                mesh_data = [mesh_data]
            
            for mesh in mesh_data:
                if isinstance(mesh, dict) and "descriptorName" in mesh:
                    mesh_terms.append(mesh["descriptorName"])
        
        return mesh_terms
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="europepmc-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities()
                )
            )


async def main():
    """Main entry point for the server."""
    server = EuropePMCServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
