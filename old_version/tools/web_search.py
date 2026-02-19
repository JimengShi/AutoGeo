"""
LLM-Powered Web Search for Datasets
Uses LLM to search the web and find datasets
"""

import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class LLMWebSearcher:
    """LLM-powered web searcher for finding datasets"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", provider: str = "openai"):
        """
        Initialize the LLM web searcher
        
        Args:
            api_key: API key for LLM service
            model: LLM model name
            provider: LLM provider ('openai', 'anthropic')
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.provider = provider.lower()
        
        if not self.api_key:
            raise ValueError("LLM API key required. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        
        # Initialize LLM client
        if self.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")

        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"LLMWebSearcher initialized with model: {model}")
    

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for datasets using LLM web search
        
        Args:
            query: Search query
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of dictionaries with name, description, and source
        """
        try:
            logger.info(f"Searching for datasets using LLM: '{query}'")
            
            # Create prompt for LLM to search and find datasets
            prompt = f"""
                Search the web and find {limit} datasets related to: "{query}".

                For each dataset, provide:
                1. Dataset name
                2. Brief description (1-2 sentences) on the data variables provided and temporal/spatial information if available
                3. Source/website link or organization name

                Return the results as a structured list. Focus on:
                    - HuggingFace datasets (https://huggingface.co/datasets/)
                    - Kaggle datasets (https://www.kaggle.com/datasets)
                    - Academic datasets
                    - Government/open data portals
                    - Other public dataset repositories

                Format your response as a JSON-like list with this structure:
                [
                    {{
                        "name": "dataset_name",
                        "description": "brief description",
                        "source": "https://website.com/dataset or organization name"
                    }},
                    ...
                ]

                Return exactly {limit} results.
            """

            # Call LLM
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that searches the web to find datasets. Return results in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                generated_text = response.choices[0].message.content

            elif self.provider == "anthropic":
            # else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system="You are a helpful assistant that searches the web to find datasets. Return results in JSON format.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                generated_text = response.content[0].text
            
            # Parse the response
            results = self._parse_llm_response(generated_text, limit)
            
            logger.info(f"Found {len(results)} datasets via LLM web search")
            return results
            
        except Exception as e:
            logger.error(f"Error in LLM web search: {e}")
            raise RuntimeError(f"LLM web search failed: {str(e)}")
    
    def _parse_llm_response(self, text: str, limit: int) -> List[Dict[str, Any]]:
        """Parse LLM response to extract dataset information"""
        import json
        import re
        
        results = []
        
        # Try to extract JSON from the response
        # Look for JSON array pattern
        json_match = re.search(r'\[.*?\]', text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    for item in parsed[:limit]:
                        if isinstance(item, dict):
                            results.append({
                                "name": item.get("name", "Unknown"),
                                "description": item.get("description", "No description available"),
                                "source": item.get("source", "Unknown")
                            })
                    return results
            except json.JSONDecodeError:
                pass
        
        # Fallback: Try to parse line by line
        lines = text.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for name
            if 'name' in line.lower() or 'dataset' in line.lower():
                name_match = re.search(r'["\']?([^"\']+)["\']?', line)
                if name_match and not current_item.get('name'):
                    current_item['name'] = name_match.group(1)
            
            # Look for description
            if 'description' in line.lower() or 'desc' in line.lower():
                desc_match = re.search(r'["\']?([^"\']+)["\']?', line)
                if desc_match:
                    current_item['description'] = desc_match.group(1)
            
            # Look for source/url
            if 'source' in line.lower() or 'url' in line.lower() or 'http' in line.lower():
                url_match = re.search(r'(https?://[^\s"\']+)', line)
                if url_match:
                    current_item['source'] = url_match.group(1)
                else:
                    source_match = re.search(r'["\']?([^"\']+)["\']?', line)
                    if source_match:
                        current_item['source'] = source_match.group(1)
            
            # If we have all fields, add to results
            if current_item.get('name') and len(current_item) >= 2:
                results.append({
                    "name": current_item.get('name', 'Unknown'),
                    "description": current_item.get('description', 'No description available'),
                    "source": current_item.get('source', 'Unknown')
                })
                current_item = {}
                if len(results) >= limit:
                    break
        
        # If we still don't have results, create from text
        if not results:
            # Try to extract any URLs and dataset names mentioned
            urls = re.findall(r'(https?://[^\s]+)', text)
            for i, url in enumerate(urls[:limit]):
                # Try to find dataset name near the URL
                name = f"Dataset {i+1}"
                # Look for text before the URL
                url_pos = text.find(url)
                if url_pos > 0:
                    before_text = text[max(0, url_pos-50):url_pos]
                    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', before_text)
                    if name_match:
                        name = name_match.group(1)
                
                results.append({
                    "name": name,
                    "description": "Dataset found via web search",
                    "source": url
                })
        
        return results[:limit]
