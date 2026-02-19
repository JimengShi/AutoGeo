# Data Processing Agent (LLM-Powered)

A comprehensive data processing agent with a **chatbot interface** that uses **Large Language Models (LLMs)** to generate and execute code for searching, downloading, and processing datasets. The agent dynamically generates Python code based on your requests and executes it safely.


## Features
The agent uses a **code generation and execution** approach:
- **🤖 LLM-Powered Code Generation**: Uses ChatGPT/Claude to generate code for data processing tasks
- **💬 Chatbot Interface**: Interactive natural language interface for easy interaction
- **🔍 Dynamic Search**: LLM generates code to search datasets from multiple sources (HuggingFace, Kaggle)
- **⬇️ Dynamic Download**: LLM generates code to download datasets from various sources
- **⚙️ Dynamic Processing**: LLM generates code to clean, analyze, and transform datasets
- **🔄 Complete Pipeline**: Run search-download-process pipeline with LLM-generated code
- **🔒 Safe Execution**: Code execution engine with security measures


<!-- ## Module Structure

- `chatbot.py`: **Interactive chatbot interface** (main entry point)
- `llm_agent.py`: **LLM-powered agent** that generates and executes code
- `llm_client.py`: **LLM client** for code generation (OpenAI/Anthropic)
- `code_executor.py`: **Safe code execution engine** with security measures
- `agent.py`: Original agent class (kept for reference)
- `search.py`: Original search module (kept for reference)
- `download.py`: Original download module (kept for reference)
- `process.py`: Original process module (kept for reference)
- `config.py`: Configuration management
- `example.py`: Example script that starts the chatbot -->


## Installation

1. **Install dependencies:** `pip install -r requirements.txt`

2. **Set up API key (required)**:
     ```bash
     export OPENAI_API_KEY="sk-proj-xxxx"    # OPENAI_API_KEY
     export ANTHROPIC_API_KEY="sk-ant-xxxx"  # ANTHROPIC_API_KEY
     export TAVILY_API_KEY="tvly-dev-xxxx"   # TAVILY_API_KEY for web search
     ```


3. (Optional) For Kaggle integration, set up Kaggle API credentials:
   - Go to https://www.kaggle.com/account
   - Create an API token
   - Place `kaggle.json` in `~/.kaggle/` directory

4. (Optional) For HuggingFace integration, optionally set up authentication:
   ```bash
   huggingface-cli login
    ```



## Quick Start: Interactive Chatbot 🤖

### 0. Start Chatbot
From the project root path, run

```bash
python run_geoagent.py
```

Then interact naturally.

### 1. Data Search
- ✅ LLM-based search
- ✅ Web-based search


```
You: search 3 datasets on flood risks

Bot: 🔄 Processing workflow...

📋 Workflow Plan (1 steps):
   1. search: Search for geospatial datasets related to: search 5 datasets...

🔍 Step 1/1: Searching for datasets...
======================================================================
Workflow Results
======================================================================
✅ Workflow completed successfully!

🔍 Search Results:

   1. Flood Hazard Mapping
      Description: This dataset provides flood hazard maps based on historical flood data and modeling, covering the continental United States....
      Source: {'url': 'https://www.fema.gov/flood-maps', 'data_source': 'FEMA'}

   2. Global Flood Monitoring System
      Description: A global dataset that monitors flood events using satellite imagery, providing near real-time flood extent information....
      Source: {'url': 'https://www.jrc.ec.europa.eu/en/research-facility/global-flood-monitoring-system', 'data_source': 'European Commission Joint Research Centre'}

   3. NASA MODIS Flood Products
      Description: MODIS satellite data providing flood extent and severity information, with daily updates and global coverage....
      Source: {'url': 'https://modis.gsfc.nasa.gov/data/dataprod/flood/', 'data_source': 'NASA Earthdata'}

💬 Workflow Messages:
   - search 3 datasets on flood risks
   - Workflow planned with 1 steps: search
   - search 3 datasets on flood risks
   - Workflow planned with 1 steps: search
   - Search completed: found 3 results

======================================================================
```

### 2. Data download from various data sources 
- ✅ URL, 
   - url of file: https://github.com/JimengShi/DL-WaLeF/blob/main/data/Merged-update_hourly.csv
   - url of file folder: https://github.com/JimengShi/DL-WaLeF/tree/main/data
- ✅ HuggingFace, e.g., https://huggingface.co/datasets/HC-85/flood-prediction
- ✅ Zenodo: e.g., https://zenodo.org/records/14715390
- Domain databases:
   - **USGS EarthExplorer**: Landsat, MODIS, ASTER
   - **Sentinel Hub**: Sentinel-2, Sentinel-1
   - **OpenStreetMap**: Vector data
   - **NASA Earthdata**: Various satellite products
   - **NOAA**: Weather and climate data
   - **US Census**: Demographic data



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



## Technology Stack

- **LangChain**: Agent framework and LLM integration
- **LangGraph**: Workflow orchestration and state management
- **Tavily**: Advanced web search for data discovery
- **GeoPandas**: Vector data operations
- **Rasterio**: Raster data handling
- **Shapely**: Geometric operations
- **Folium**: Interactive maps
- **Contextily**: Basemap tiles



## Extending the System

To add a new agent:

1. Create agent class in `geospatial_agents/agents/`
2. Inherit from base pattern (see existing agents)
3. Add node to workflow in `orchestrator_langgraph.py`
4. Implement `execute()` method with LLM code generation

## License

MIT

