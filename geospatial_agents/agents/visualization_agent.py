"""
Visualization Agent
Creates maps and visualizations
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)


class VisualizationAgent:
    """Agent for creating geospatial visualizations"""
    
    def __init__(
        self,
        llm: BaseChatModel,
        work_dir: Path = None
    ):
        """
        Initialize visualization agent
        
        Args:
            llm: Language model instance
            work_dir: Working directory
        """
        self.llm = llm
        self.work_dir = work_dir or Path("./geospatial_data")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir = self.work_dir / "visualizations"
        self.viz_dir.mkdir(exist_ok=True)
    
    def execute(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute visualization task
        
        Args:
            task_description: Description of visualization task
            parameters: Visualization parameters
            context: Context with data to visualize
            
        Returns:
            Visualization file path
        """
        logger.info(f"Executing visualization: {task_description}")
        
        data_paths = self._get_data_paths(context)
        
        if not data_paths:
            logger.warning("No data files found in context. Visualization requires downloaded or processed data.")
            logger.warning("Available context keys: " + str(list(context.keys()) if context else []))
            return {
                "visualization_path": None, 
                "error": "No data available for visualization. Please download or process data first."
            }
        
        code = self._generate_visualization_code(
            task_description,
            parameters,
            data_paths
        )
        
        viz_path = self._execute_visualization(code, data_paths)
        
        return {
            "visualization_path": viz_path,
            "visualization_type": parameters.get("type", "map")
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
    
    def _generate_visualization_code(
        self,
        task_description: str,
        parameters: Dict[str, Any],
        data_paths: list
    ) -> str:
        """Generate visualization code using LLM"""
        prompt = f"""Generate Python code to create this visualization: "{task_description}"

Parameters: {json.dumps(parameters, indent=2)}
Data files: {[str(p) for p in data_paths]}

The code should:
1. Load geospatial data
2. Create appropriate visualization (static map, interactive map, choropleth, etc.)
3. Save visualization to: {self.viz_dir / 'visualization.html'}

Use:
- folium for interactive maps
- matplotlib/contextily for static maps
- geopandas for data handling

Return only executable Python code.
"""
        
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="You are a geospatial visualization expert. Generate executable Python code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content
        
        code_match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if code_match:
            code = code_match.group(1)
        
        return code
    
    def _execute_visualization(self, code: str, data_paths: list) -> Optional[Path]:
        """Execute visualization code"""
        try:
            import geopandas as gpd
            import folium
            import matplotlib.pyplot as plt
            import contextily as ctx
            
            exec_globals = {
                "gpd": gpd,
                "folium": folium,
                "plt": plt,
                "matplotlib": __import__("matplotlib"),
                "contextily": ctx,
                "Path": Path,
                "self": self,
                "data_paths": data_paths,
                "logger": logger
            }
            
            exec(code, exec_globals)
            return exec_globals.get("viz_path") or exec_globals.get("output_path")
        except Exception as e:
            logger.error(f"Visualization execution failed: {e}")
            return None
