"""
Spatial Query Agent
Performs spatial filtering and queries on geospatial data
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class SpatialQueryAgent:
    """Agent for spatial queries and filtering"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize spatial query agent
        
        Args:
            llm: Language model instance
            work_dir: Working directory
        """
        self.llm = llm
        self.work_dir = work_dir or Path("./geospatial_data")
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute spatial query task
        
        Args:
            task_description: Description of spatial query
            parameters: Query parameters (bbox, geometry, operation, etc.)
            context: Context with downloaded data
            
        Returns:
            Filtered geospatial data
        """
        logger.info(f"Executing spatial query: {task_description}")
        
        # Get data to query from context
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            return {"filtered_data": None, "error": "No data available for spatial query"}
        
        # Use LLM to generate spatial query code
        code = self._generate_spatial_query_code(
            task_description,
            parameters,
            data_paths
        )
        
        # Execute spatial query
        filtered_data = self._execute_spatial_query(code, data_paths)
        
        return {
            "filtered_data": filtered_data,
            "query_description": task_description
        }
    
    def _get_data_paths(self, context: Dict[str, Any]) -> list:
        """Extract data file paths from context"""
        paths = []
        
        if context:
            # From downloaded data
            if "downloaded_data" in context:
                paths.extend(context["downloaded_data"].values())
            
            # From processed data
            if "processed_data" in context:
                for data in context["processed_data"].values():
                    if isinstance(data, (str, Path)):
                        paths.append(data)
        
        return [Path(p) for p in paths if Path(p).exists()]
    
    def _generate_spatial_query_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list
    ) -> str:
        """Generate spatial query code using LLM"""
        prompt = f"""Generate Python code to perform this spatial query: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}

The code should:
1. Load geospatial data (GeoPandas for vector, Rasterio for raster)
2. Perform the spatial operation (clip, buffer, intersect, within, etc.)
3. Handle coordinate reference systems
4. Save filtered result to: {self.work_dir / 'filtered_data.geojson'}

Use appropriate libraries:
- geopandas for vector data operations
- rasterio for raster data operations
- shapely for geometric operations
- pyproj for coordinate transformations

Return only executable Python code, no explanations.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial analysis expert. Generate executable Python code for spatial operations."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        # Extract code block
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_spatial_query(self, code: str, data_paths: list) -> Optional[Path]:
        """Execute spatial query code"""
        try:
            import geopandas as gpd
            import rasterio
            from shapely.geometry import box, Point, Polygon
            import pyproj
            
            exec_globals = {
                "gpd": gpd,
                "geopandas": gpd,
                "rasterio": rasterio,
                "box": box,
                "Point": Point,
                "Polygon": Polygon,
                "pyproj": pyproj,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "logger": logger
            }
            
            exec(code, exec_globals)
            
            # Return path to filtered data
            return exec_globals.get("result_path") or exec_globals.get("output_path")
        except Exception as e:
            logger.error(f"Spatial query execution failed: {e}")
            return None
