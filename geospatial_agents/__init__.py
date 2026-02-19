"""
GEOAGENT: Multi-Agent Orchestration for Geospatial Data Science
"""

try:
    from .orchestrator_langgraph import GeoOrchestratorLangGraph
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from geospatial_agents.orchestrator_langgraph import GeoOrchestratorLangGraph

__version__ = "0.1.0"
__all__ = ["GeoOrchestratorLangGraph"]
