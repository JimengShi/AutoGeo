"""
Process Agent
Performs geospatial data processing operations
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class ProcessAgent:
    """Agent for geospatial data processing"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize process agent
        
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
        Execute processing task
        
        Args:
            task_description: Description of processing task
            parameters: Processing parameters
            context: Context with data to process
            
        Returns:
            Processed data path
        """
        logger.info(f"Executing process: {task_description}")
        
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            return {"processed_data": None, "error": "No data available for processing"}
        
        code = self._generate_process_code(
            task_description,
            parameters,
            data_paths
        )
        
        processed_path = self._execute_process(code, data_paths)
        
        return {
            "processed_data": processed_path,
            "processing_type": parameters.get("type", "general")
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
    
    def _generate_process_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list
    ) -> str:
        """Generate processing code using LLM"""
        prompt = f"""Generate Python code to perform this geospatial processing: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}

The code should:
1. Load geospatial data
2. Perform processing operations (spatial join, buffer, overlay, zonal statistics, etc.)
3. Save processed data to: {self.work_dir / 'processed_data'}

Use:
- geopandas for vector operations
- rasterio for raster operations
- shapely for geometric operations

Return only executable Python code.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial processing expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_process(self, code: str, data_paths: list) -> Optional[Path]:
        """Execute processing code"""
        try:
            import geopandas as gpd
            import rasterio
            from shapely.geometry import Point, Polygon, LineString
            import numpy as np
            import pandas as pd
            
            exec_globals = {
                "gpd": gpd,
                "geopandas": gpd,
                "rasterio": rasterio,
                "Point": Point,
                "Polygon": Polygon,
                "LineString": LineString,
                "np": np,
                "pandas": pd,
                "pd": pd,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "logger": logger
            }
            
            exec(code, exec_globals)
            return exec_globals.get("result_path") or exec_globals.get("output_path")
        except Exception as e:
            logger.error(f"Process execution failed: {e}")
            return None
