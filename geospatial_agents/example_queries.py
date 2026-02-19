"""
Example queries for GEOAGENT
Demonstrates various types of datasets and processing operations
"""

# ============================================================================
# DATASET DOWNLOAD EXAMPLES
# ============================================================================

DOWNLOAD_EXAMPLES = {
    "satellite_imagery": [
        "Download Landsat 8 imagery for California from 2023",
        "Get Sentinel-2 imagery for Amazon rainforest 2024",
        "Download MODIS land surface temperature data for Africa",
    ],
    
    "elevation_data": [
        "Download SRTM elevation data for the Rocky Mountains",
        "Get ASTER GDEM data for Japan",
        "Download high-resolution DEM for Grand Canyon",
    ],
    
    "vector_data": [
        "Download country boundaries from Natural Earth",
        "Get US state and county boundaries",
        "Download OpenStreetMap road network for California",
    ],
    
    "climate_data": [
        "Download global precipitation data from CHIRPS",
        "Get daily rainfall data for India monsoon season",
        "Download global temperature data from NOAA",
    ],
    
    "flood_data": [
        "Download flood extent data from Dartmouth Flood Observatory",
        "Get historical flood records for river basins",
        "Download flood risk maps for coastal areas",
    ],
    
    "population_data": [
        "Download WorldPop population density data",
        "Get census block population data for cities",
        "Download demographic data from US Census Bureau",
    ],
}

# ============================================================================
# PROCESSING OPERATION EXAMPLES
# ============================================================================

PROCESSING_EXAMPLES = {
    "spatial_queries": [
        "Clip the satellite imagery to California boundaries",
        "Create a 5km buffer around all hospitals",
        "Find all buildings that intersect with flood zones",
    ],
    
    "transformations": [
        "Reproject the data from WGS84 to UTM Zone 10N",
        "Convert Shapefile to GeoJSON",
        "Resample the raster to 100m resolution",
    ],
    
    "raster_processing": [
        "Calculate NDVI from satellite imagery",
        "Mosaic multiple Landsat scenes into a single image",
        "Calculate slope and aspect from elevation data",
    ],
    
    "vector_processing": [
        "Join population data to administrative boundaries",
        "Calculate area of each polygon",
        "Dissolve county boundaries to create state boundaries",
    ],
    
    "temporal_analysis": [
        "Analyze land use change from 2010 to 2024",
        "Detect deforestation between two time periods",
        "Calculate monthly average temperature trends",
    ],
    
    "advanced_analysis": [
        "Identify clusters of high population density",
        "Interpolate temperature measurements to create a surface",
        "Calculate shortest path between two locations",
    ],
    
    "visualization": [
        "Create a choropleth map of population density",
        "Generate an interactive map with Folium",
        "Create a map showing elevation with hillshade",
    ],
}

# ============================================================================
# COMPLETE WORKFLOW EXAMPLES
# ============================================================================

WORKFLOW_EXAMPLES = [
    {
        "name": "Flood Risk Assessment",
        "query": "Assess flood risk for areas within 5km of major rivers in Texas using elevation and precipitation data. Create a risk map and export the results.",
        "description": "Complete workflow from data search to risk analysis and visualization"
    },
    {
        "name": "Urban Heat Island Analysis",
        "query": "Analyze urban heat islands in New York City. Download land surface temperature data and land cover data, compare temperatures in urban vs rural areas, and create a heat map.",
        "description": "Multi-dataset analysis with spatial comparison"
    },
    {
        "name": "Deforestation Monitoring",
        "query": "Monitor deforestation in the Amazon from 2020 to 2024. Download Landsat imagery for both time periods, classify land cover, detect changes, and create a change map.",
        "description": "Temporal analysis with change detection"
    },
    {
        "name": "Population Density Analysis",
        "query": "Analyze population density in California. Download census population data, join with administrative boundaries, calculate density per square kilometer, and create a choropleth map.",
        "description": "Vector data processing with statistical analysis"
    },
    {
        "name": "Land Use Classification",
        "query": "Classify land use from satellite imagery for California. Download Landsat imagery, perform supervised classification, and create a land use map.",
        "description": "Machine learning-based classification"
    },
]

# ============================================================================
# QUICK START EXAMPLES
# ============================================================================

QUICK_START = [
    "Show me 5 datasets on flood monitoring",
    "Find and download OpenStreetMap data for California",
    "Find elevation data for Colorado, clip to state boundaries, and create a hillshade map",
    "Analyze land use change in Texas from 2020 to 2024",
]

# ============================================================================
# PRINT EXAMPLES
# ============================================================================

def print_examples():
    """Print all example queries"""
    print("=" * 80)
    print("GEOAGENT EXAMPLE QUERIES")
    print("=" * 80)
    print()
    
    print("📥 DATASET DOWNLOAD EXAMPLES")
    print("-" * 80)
    for category, examples in DOWNLOAD_EXAMPLES.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for example in examples:
            print(f"  • {example}")
    print()
    
    print("⚙️  PROCESSING OPERATION EXAMPLES")
    print("-" * 80)
    for category, examples in PROCESSING_EXAMPLES.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for example in examples:
            print(f"  • {example}")
    print()
    
    print("🔄 COMPLETE WORKFLOW EXAMPLES")
    print("-" * 80)
    for workflow in WORKFLOW_EXAMPLES:
        print(f"\n{workflow['name']}:")
        print(f"  Description: {workflow['description']}")
        print(f"  Query: {workflow['query']}")
    print()
    
    print("🚀 QUICK START EXAMPLES")
    print("-" * 80)
    for example in QUICK_START:
        print(f"  • {example}")
    print()


if __name__ == "__main__":
    print_examples()
