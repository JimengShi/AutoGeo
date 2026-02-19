# GEOAGENT Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r geospatial_agents/requirements.txt
```

2. **Set up API keys:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export TAVILY_API_KEY="your-tavily-api-key"  # Optional but recommended
```

Get Tavily API key: https://tavily.com/

## Quick Test

```python
from geospatial_agents import GeoOrchestratorLangGraph
import os

# Initialize
orchestrator = GeoOrchestratorLangGraph(
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

# Execute a workflow
result = orchestrator.execute(
    "Find parks within 5 miles of downtown Seattle"
)

print(result)
```

## Run Interactive Mode

**Option 1: From project root (recommended):**
```bash
python run_geoagent.py
```

**Option 2: Using module syntax:**
```bash
python -m geospatial_agents.main
```

**Option 3: From within geospatial_agents directory:**
```bash
cd geospatial_agents
python main.py
```

## Example Queries

### Simple Queries
- "Show me 5 datasets on flood monitoring"
- "Find all parks within 5 miles of downtown Seattle"
- "Download Landsat imagery for California from 2023"

### Processing Queries
- "Clip satellite imagery to California boundaries"
- "Reproject data from WGS84 to UTM Zone 10N"
- "Calculate NDVI from satellite imagery"

### Complete Workflows
- "Analyze land use change in California from 2020 to 2024 using satellite imagery"
- "Assess flood risk for areas within 5km of major rivers in Texas"
- "Create a population density map for New York City"

**📚 For more examples, see [EXAMPLES.md](EXAMPLES.md)**

## How It Works

1. **User Request** → Natural language input
2. **LLM Plans Workflow** → Breaks down into steps
3. **LangGraph Orchestrates** → Routes between agents
4. **Agents Execute** → Each agent performs its task
5. **Results Returned** → Final outputs, visualizations, exports

## Architecture

- **LangGraph**: Manages workflow state and routing
- **LangChain**: LLM integration for each agent
- **Tavily**: Enhanced web search for data discovery
- **GeoPandas/Rasterio**: Geospatial operations

## Troubleshooting

### Import Errors
Make sure all dependencies are installed:
```bash
pip install langchain langgraph langchain-openai tavily-python geopandas rasterio
```

### API Key Issues
- Check environment variables are set
- Verify API keys are valid
- Tavily key is optional but improves search quality

### Geospatial Library Errors
- Ensure GDAL is installed (required for GeoPandas/Rasterio)
- On Linux: `sudo apt-get install gdal-bin libgdal-dev`
- On Mac: `brew install gdal`
- Then: `pip install geopandas rasterio`
