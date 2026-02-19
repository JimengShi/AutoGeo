# GEOAGENT: Multi-Agent Geospatial Data Science System

A multi-agent orchestration system for complex geospatial data science workflows, built with LangChain, LangGraph, and Tavily.

## Features

- 🤖 **Multi-Agent Architecture**: 8 specialized agents working together
- 🔄 **LangGraph Orchestration**: State-based workflow management
- 🔍 **Tavily Integration**: Advanced web search for geospatial data discovery
- 🗺️ **Geospatial Operations**: Spatial queries, transformations, analysis, and visualization
- 💬 **Natural Language Interface**: Describe your workflow in plain English
- 🧠 **LLM-Powered**: Uses LLM to understand requests and generate code

## Architecture

The system uses **LangGraph** to orchestrate multiple specialized agents:

1. **Search Agent**: Finds geospatial datasets using Tavily and LLM
2. **Download Agent**: Downloads data from various sources
3. **Spatial Query Agent**: Performs spatial filtering and queries
4. **Transform Agent**: Handles CRS and format transformations
5. **Process Agent**: Performs geospatial processing operations
6. **Analysis Agent**: Advanced spatial analysis and ML
7. **Visualization Agent**: Creates maps and visualizations
8. **Export Agent**: Exports data in various formats

## Installation

1. Install dependencies:

```bash
pip install -r geospatial_agents/requirements.txt
```

2. Set up API keys:

```bash
export OPENAI_API_KEY="your-openai-key"
export TAVILY_API_KEY="your-tavily-key"  # Optional but recommended
```

## Quick Start

```python
from geospatial_agents import GeoOrchestratorLangGraph
import os

# Initialize orchestrator
orchestrator = GeoOrchestratorLangGraph(
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    llm_model="gpt-4o-mini",
    llm_provider="openai",
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

# Execute workflow
result = orchestrator.execute(
    "Find all parks within 5 miles of downtown Seattle and create a map"
)

print(f"Success: {result['success']}")
print(f"Outputs: {result['final_outputs']}")
```

## Interactive Mode

Run the interactive interface:

**From project root (recommended):**
```bash
python run_geoagent.py
```

**Or using module syntax:**
```bash
python -m geospatial_agents.main
```

Then interact naturally:

```
You: Find flood risk areas in Texas using elevation data
You: Analyze land use change in California from 2020 to 2024
You: Create a population density map for New York City
```

## Example Workflows

### Quick Examples

**Simple Search:**
```python
result = orchestrator.execute("Show me 5 datasets on flood monitoring")
```

**Search and Download:**
```python
result = orchestrator.execute("Find and download OpenStreetMap data for California")
```

**Complete Analysis:**
```python
result = orchestrator.execute(
    "Analyze land use change in California from 2020 to 2024 using satellite imagery"
)
```

### More Examples

See **[EXAMPLES.md](EXAMPLES.md)** for comprehensive examples including:
- 📥 **Downloadable Datasets**: Satellite imagery, elevation data, vector data, climate data, flood data, population data
- ⚙️ **Processing Operations**: Spatial queries, transformations, raster/vector processing, temporal analysis, ML operations
- 🔄 **Complete Workflows**: End-to-end examples from data search to visualization

You can also run:
```bash
python geospatial_agents/example_queries.py
```
to see all available example queries.

## Agent Details

### Search Agent
- Uses **Tavily** for web search
- Enhances results with geospatial metadata via LLM
- Identifies data sources (USGS, NASA, OpenStreetMap, etc.)

### Download Agent
- Downloads from URLs, HuggingFace, APIs
- Handles authentication
- Extracts compressed files
- Uses LLM to generate download code when needed

### Spatial Query Agent
- Performs spatial operations (clip, buffer, intersect, within)
- Handles CRS transformations
- Generates GeoPandas/Rasterio code via LLM

### Transform Agent
- Reprojects between coordinate systems
- Converts formats (raster ↔ vector)
- Resamples raster data
- Uses LLM for transformation code generation

### Process Agent
- Spatial joins and overlays
- Proximity calculations
- Zonal statistics
- Buffer operations

### Analysis Agent
- Spatial clustering
- Land use classification
- Temporal analysis
- ML-based geospatial analysis

### Visualization Agent
- Creates static maps (Matplotlib + Contextily)
- Creates interactive maps (Folium)
- Choropleth maps
- Custom styling

### Export Agent
- Exports to GeoJSON, Shapefile, GeoTIFF, CSV, Parquet
- Preserves CRS and metadata
- Handles format conversions

## Workflow State Management

LangGraph maintains state throughout the workflow:

```python
class WorkflowState(TypedDict):
    user_request: str
    workflow_plan: list
    search_results: list
    downloaded_data: dict
    processed_data: dict
    analysis_results: dict
    visualizations: list
    exports: list
    errors: list
    messages: list
    final_outputs: list
```

## Technology Stack

- **LangChain**: Agent framework and LLM integration
- **LangGraph**: Workflow orchestration and state management
- **Tavily**: Advanced web search for data discovery
- **GeoPandas**: Vector data operations
- **Rasterio**: Raster data handling
- **Shapely**: Geometric operations
- **Folium**: Interactive maps
- **Contextily**: Basemap tiles

## Configuration

```python
orchestrator = GeoOrchestratorLangGraph(
    llm_api_key="your-key",
    llm_model="gpt-4o-mini",  # or "gpt-4", "claude-3-opus"
    llm_provider="openai",  # or "anthropic"
    tavily_api_key="your-tavily-key",  # Optional
    work_dir="./geospatial_data"  # Data storage directory
)
```

## Error Handling

The system includes:
- Automatic error recovery
- Dependency checking between workflow steps
- Progress tracking
- Detailed error messages

## Extending the System

To add a new agent:

1. Create agent class in `geospatial_agents/agents/`
2. Inherit from base pattern (see existing agents)
3. Add node to workflow in `orchestrator_langgraph.py`
4. Implement `execute()` method with LLM code generation

## License

MIT
