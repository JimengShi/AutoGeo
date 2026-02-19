"""
Transform Agent
Handles coordinate system and format transformations
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class TransformAgent:
    """Agent for coordinate and format transformations"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize transform agent
        
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
        Execute transformation task
        
        Args:
            task_description: Description of transformation
            parameters: Transform parameters (target_crs, format, etc.)
            context: Context with data to transform
            
        Returns:
            Transformed data path
        """
        logger.info(f"Executing transform: {task_description}")
        
        # Get data to transform
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            return {"transformed_data": None, "error": "No data available for transformation"}
        
        # Generate transformation code
        code = self._generate_transform_code(
            task_description,
            parameters,
            data_paths
        )
        
        # Execute transformation
        transformed_path = self._execute_transform(code, data_paths)
        
        return {
            "transformed_data": transformed_path,
            "transformation_type": parameters.get("type", "reproject")
        }
    
    def _get_data_paths(self, context: Dict[str, Any]) -> list:
        """Extract data paths from context"""
        paths = []
        if context:
            if "downloaded_data" in context:
                paths.extend(context["downloaded_data"].values())
            if "processed_data" in context:
                for data in context["processed_data"].values():
                    if isinstance(data, (str, Path)):
                        paths.append(data)
        return [Path(p) for p in paths if Path(p).exists()]
    
    def _generate_transform_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list
    ) -> str:
        """Generate transformation code using LLM"""
        prompt = f"""Generate Python code to perform this transformation: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}

The code should:
1. Load geospatial data
2. Perform transformation (reproject, format conversion, resample, etc.)
3. Save transformed data to: {self.work_dir / 'transformed_data'}

Use:
- geopandas for vector CRS transformations
- rasterio for raster CRS transformations
- pyproj for coordinate system definitions

Return only executable Python code.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial transformation expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_transform(self, code: str, data_paths: list) -> Optional[Path]:
        """Execute transformation code"""
        try:
            import geopandas as gpd
            import rasterio
            from rasterio.warp import calculate_default_transform, reproject, Resampling
            import pyproj
            
            exec_globals = {
                "gpd": gpd,
                "rasterio": rasterio,
                "calculate_default_transform": calculate_default_transform,
                "reproject": reproject,
                "Resampling": Resampling,
                "pyproj": pyproj,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "logger": logger
            }
            
            exec(code, exec_globals)
            return exec_globals.get("result_path") or exec_globals.get("output_path")
        except Exception as e:
            logger.error(f"Transform execution failed: {e}")
            return None
