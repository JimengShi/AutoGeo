"""
Search Agent for Geospatial Data
Uses Tavily and LLM to find geospatial datasets
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class SearchAgent:
    """Agent for searching geospatial datasets"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        tavily_api_key: Optional[str] = None,
        work_dir: Path = None
    ):
        """
        Initialize search agent
        
        Args:
            llm: Language model instance
            tavily_api_key: Tavily API key
            work_dir: Working directory
        """
        self.llm = llm
        self.work_dir = work_dir or Path("./geospatial_data")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Tavily if API key provided
        self.tavily_client = None
        if tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily: {e}")
    
    def execute(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute search task
        
        Args:
            task_description: Description of the search task
            parameters: Search parameters
            context: Context from previous steps
            
        Returns:
            Search results
        """
        logger.info(f"Executing search: {task_description}")
        
        query = parameters.get("query", task_description)
        data_type = parameters.get("data_type", "auto")
        limit = parameters.get("limit", 5)
        
        if limit != 5:
            logger.info(f"Using custom limit: {limit} (requested by user)")
        
        # Use Tavily for web search
        if self.tavily_client:
            results = self._search_with_tavily(query, limit)
        else:
            # Fallback to LLM-based search
            results = self._search_with_llm(query, limit)
        
        # Enhance results with LLM for geospatial context
        enhanced_results = self._enhance_results_with_llm(results, query, data_type)
        
        return {
            "results": enhanced_results,
            "count": len(enhanced_results)
        }
    
    def _search_with_tavily(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        try:
            # Add geospatial context to query
            geospatial_query = f"{query} geospatial data dataset download"
            
            response = self.tavily_client.search(
                query=geospatial_query,
                search_depth="advanced",
                max_results=limit
            )
            
            results = []
            for item in response.get("results", [])[:limit]:
                url = item.get("url", "")
                # Keep source as simple string URL for compatibility
                results.append({
                    "name": item.get("title", "Unknown"),
                    "description": item.get("content", "")[:200],
                    "source": url,  # Keep as string, not dict
                    "score": item.get("score", 0.0)
                })
            
            return results
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    def _search_with_llm(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using LLM knowledge"""
        prompt = f"""
            Find {limit} geospatial datasets related to: "{query}"
            Focus on these major geospatial databases:
            - USGS EarthExplorer: Landsat, MODIS, ASTER, SRTM
            - NASA Earthdata: MODIS, VIIRS, GPM, climate data
            - Copernicus Open Access Hub: Sentinel-1, Sentinel-2, Sentinel-3
            - OpenStreetMap: Road networks, buildings, POIs, boundaries
            - Natural Earth: Country/state boundaries, coastlines, cultural features
            - NOAA: Climate, weather, ocean, hurricane data
            - US Census Bureau: Population, demographics, census boundaries
            - WorldPop: Population density and counts
            - OpenTopography: LiDAR, high-resolution DEMs, SRTM
            - Global Forest Watch: Forest cover, deforestation, tree cover loss
            - Dartmouth Flood Observatory: Flood extent, historical floods
            - HuggingFace Datasets: Preprocessed geospatial datasets
            - Academic geospatial datasets
            - Government open data portals

            For each dataset, provide:
            - name: Dataset name
            - description: Brief description with spatial/temporal coverage
            - source: URL and data source name
            - data_type: Type of data (satellite, vector, raster, etc.)

            Return as JSON array.
        """
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are an expert in geospatial data sources. Return results in JSON format."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content
        
        # Parse JSON response
        try:
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))[:limit]
        except Exception as e:
            logger.warning(f"Failed to parse LLM search results: {e}")
        
        return []
    
    def _enhance_results_with_llm(
        self,
        results: List[Dict[str, Any]],
        query: str,
        data_type: str
    ) -> List[Dict[str, Any]]:
        """Enhance search results with geospatial metadata using LLM"""
        if not results:
            return results
        
        prompt = f"""Enhance these geospatial dataset search results for query: "{query}"
            Results:
            {json.dumps(results, indent=4)}

            For each result, add/update:
            - spatial_coverage: Geographic area covered (e.g., "California, USA", "Global")
            - temporal_coverage: Time period (e.g., "2020-2024", "Monthly")
            - coordinate_system: CRS if known (e.g., "WGS84", "UTM Zone 10N")
            - download_method: How to access (e.g., "API", "Direct download", "HuggingFace")
            - file_formats: Expected formats (e.g., "GeoTIFF", "Shapefile", "GeoJSON")

            Return enhanced JSON array.
        """
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial data expert. Enhance results with spatial metadata."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        text = response.content
        
        try:
            json_match = re.search(r'\[.*?\]', text, re.DOTALL)
            if json_match:
                enhanced = json.loads(json_match.group(0))
                # Merge with original results, but preserve source as string
                for i, result in enumerate(enhanced):
                    if i < len(results):
                        # If enhanced result has source as dict, extract URL
                        if isinstance(result.get("source"), dict):
                            source_dict = result.get("source", {})
                            source_url = source_dict.get("url", "")
                            if source_url:
                                result["source"] = source_url
                        # Update other fields
                        results[i].update(result)
                        # Ensure source is always a string
                        if isinstance(results[i].get("source"), dict):
                            source_dict = results[i].get("source", {})
                            results[i]["source"] = source_dict.get("url", str(source_dict))
        except Exception as e:
            logger.warning(f"Failed to enhance results: {e}")
        
        return results
