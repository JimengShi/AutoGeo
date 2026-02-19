"""
Export Agent
Handles exporting geospatial data in various formats
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class ExportAgent:
    """Agent for exporting geospatial data"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize export agent
        
        Args:
            llm: Language model instance
            work_dir: Working directory
        """
        self.llm = llm
        self.work_dir = work_dir or Path("./geospatial_data")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir = self.work_dir / "exports"
        self.exports_dir.mkdir(exist_ok=True)
    
    def execute(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute export task
        
        Args:
            task_description: Description of export task
            parameters: Export parameters (format, path, etc.)
            context: Context with data to export
            
        Returns:
            Export file path
        """
        logger.info(f"Executing export: {task_description}")
        
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            logger.warning("No data files found in context. Export requires downloaded or processed data.")
            logger.warning("Available context keys: " + str(list(context.keys()) if context else []))
            return {
                "export_path": None, 
                "error": "No data available for export. Please download or process data first."
            }
        
        export_format = parameters.get("format", "geojson")
        output_name = parameters.get("name", "exported_data")
        
        code = self._generate_export_code(
            task_description,
            parameters,
            data_paths,
            export_format,
            output_name
        )
        
        export_path = self._execute_export(code, data_paths, export_format, output_name)
        
        return {
            "export_path": export_path,
            "format": export_format
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
    
    def _generate_export_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list,
        export_format: str,
        output_name: str
    ) -> str:
        """Generate export code using LLM"""
        output_path = self.exports_dir / f"{output_name}.{export_format}"
        
        prompt = f"""Generate Python code to export geospatial data: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}
Export format: {export_format}
Output path: {output_path}

The code should:
1. Load geospatial data
2. Export in the specified format ({export_format})
3. Preserve coordinate reference system and metadata
4. Save to: {output_path}

Supported formats:
- geojson: GeoJSON format
- shapefile: ESRI Shapefile
- geotiff: GeoTIFF for raster
- csv: CSV with geometry as WKT
- parquet: Parquet format

Use:
- geopandas for vector exports
- rasterio for raster exports

Return only executable Python code.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial data export expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_export(
        self,
        code: str,
        data_paths: list,
        export_format: str,
        output_name: str
    ) -> Optional[Path]:
        """Execute export code"""
        try:
            import geopandas as gpd
            import rasterio
            import pandas as pd
            
            output_path = self.exports_dir / f"{output_name}.{export_format}"
            
            exec_globals = {
                "gpd": gpd,
                "geopandas": gpd,
                "rasterio": rasterio,
                "pd": pd,
                "pandas": pd,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "output_path": output_path,
                "logger": logger
            }
            
            exec(code, exec_globals)
            return exec_globals.get("result_path") or output_path
        except Exception as e:
            logger.error(f"Export execution failed: {e}")
            return None
