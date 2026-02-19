"""
Analysis Agent
Performs advanced geospatial analysis
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent for advanced geospatial analysis"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize analysis agent
        
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
        Execute analysis task
        
        Args:
            task_description: Description of analysis task
            parameters: Analysis parameters
            context: Context with data to analyze
            
        Returns:
            Analysis results
        """
        logger.info(f"Executing analysis: {task_description}")
        
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            return {"analysis": {}, "error": "No data available for analysis"}
        
        code = self._generate_analysis_code(
            task_description,
            parameters,
            data_paths
        )
        
        analysis_results = self._execute_analysis(code, data_paths)
        
        return {
            "analysis": analysis_results,
            "analysis_type": parameters.get("type", "general")
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
    
    def _generate_analysis_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list
    ) -> str:
        """Generate analysis code using LLM"""
        prompt = f"""Generate Python code to perform this geospatial analysis: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}

The code should:
1. Load geospatial data
2. Perform analysis (clustering, classification, statistics, etc.)
3. Return analysis results as a dictionary

Use:
- geopandas for vector analysis
- rasterio for raster analysis
- scikit-learn for ML operations
- numpy for numerical operations

Return only executable Python code that sets 'analysis_results' variable.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial analysis expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_analysis(self, code: str, data_paths: list) -> Dict[str, Any]:
        """Execute analysis code"""
        try:
            import geopandas as gpd
            import rasterio
            import numpy as np
            import pandas as pd
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            
            exec_globals = {
                "gpd": gpd,
                "rasterio": rasterio,
                "np": np,
                "pd": pd,
                "pandas": pd,
                "KMeans": KMeans,
                "StandardScaler": StandardScaler,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "logger": logger,
                "analysis_results": {}
            }
            
            exec(code, exec_globals)
            return exec_globals.get("analysis_results", {})
        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            return {"error": str(e)}
