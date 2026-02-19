# GEOAGENT Examples: Datasets and Processing Operations

This document provides examples of datasets you can download and processing operations you can perform with GEOAGENT.

## 📥 Downloadable Datasets

### 1. Satellite Imagery

**Landsat Data:**
- "Download Landsat 8 imagery for California from 2023"
- "Get Landsat 5 data for Texas between 2010 and 2015"
- "Download Landsat imagery covering New York City"

**Sentinel Data:**
- "Download Sentinel-2 imagery for Amazon rainforest 2024"
- "Get Sentinel-1 SAR data for flood monitoring in Bangladesh"
- "Download Sentinel-2 data for agricultural monitoring in Iowa"

**MODIS Data:**
- "Download MODIS land surface temperature data for Africa"
- "Get MODIS vegetation index data for global coverage"

### 2. Elevation and Terrain Data

**DEM (Digital Elevation Models):**
- "Download SRTM elevation data for the Rocky Mountains"
- "Get ASTER GDEM data for Japan"
- "Download high-resolution DEM for Grand Canyon"

**LiDAR Data:**
- "Download LiDAR point cloud data for urban areas in Seattle"
- "Get LiDAR elevation data for coastal regions"

### 3. Vector Data

**Administrative Boundaries:**
- "Download country boundaries from Natural Earth"
- "Get US state and county boundaries"
- "Download city boundaries for European cities"

**Road Networks:**
- "Download OpenStreetMap road network for California"
- "Get highway network data for the United States"

**Points of Interest:**
- "Download OpenStreetMap POI data for restaurants in New York"
- "Get hospital locations from OpenStreetMap"

### 4. Climate and Weather Data

**Precipitation:**
- "Download global precipitation data from CHIRPS"
- "Get daily rainfall data for India monsoon season"

**Temperature:**
- "Download global temperature data from NOAA"
- "Get historical temperature records for specific locations"

**Climate Indices:**
- "Download El Niño Southern Oscillation (ENSO) data"
- "Get drought index data for the United States"

### 5. Land Use and Land Cover

**Land Cover:**
- "Download CORINE land cover data for Europe"
- "Get NLCD (National Land Cover Database) for United States"
- "Download global land cover from ESA CCI"

**Land Use:**
- "Download urban land use data for major cities"
- "Get agricultural land use data for the Midwest"

### 6. Flood and Disaster Data

**Flood Data:**
- "Download flood extent data from Dartmouth Flood Observatory"
- "Get historical flood records for river basins"
- "Download flood risk maps for coastal areas"

**Disaster Data:**
- "Download earthquake epicenter data from USGS"
- "Get wildfire perimeter data for California"
- "Download hurricane track data from NOAA"

### 7. Population and Demographics

**Population Density:**
- "Download WorldPop population density data"
- "Get census block population data for cities"

**Demographics:**
- "Download demographic data from US Census Bureau"
- "Get age distribution data for urban areas"

### 8. Environmental Data

**Air Quality:**
- "Download air quality monitoring data from EPA"
- "Get satellite-based air quality data"

**Water Quality:**
- "Download water quality monitoring station data"
- "Get river water quality measurements"

## ⚙️ Data Processing Operations

### 1. Spatial Queries and Filtering

**Clip to Region:**
- "Clip the satellite imagery to California boundaries"
- "Extract data within 50km of San Francisco"
- "Filter buildings within city limits"

**Buffer Operations:**
- "Create a 5km buffer around all hospitals"
- "Find all parks within 1 mile of schools"
- "Identify areas within 10km of major rivers"

**Spatial Intersection:**
- "Find all buildings that intersect with flood zones"
- "Identify agricultural areas within protected zones"
- "Extract roads that cross state boundaries"

**Point-in-Polygon:**
- "Find all cities within a specific region"
- "Identify which census tracts contain hospitals"
- "Count points of interest within each administrative unit"

### 2. Coordinate Transformations

**Reprojection:**
- "Reproject the data from WGS84 to UTM Zone 10N"
- "Convert coordinates from geographic to projected CRS"
- "Transform data to match another dataset's coordinate system"

**Format Conversion:**
- "Convert Shapefile to GeoJSON"
- "Convert raster to vector (polygonize)"
- "Convert vector to raster (rasterize)"
- "Export data to KML format for Google Earth"

### 3. Raster Processing

**Resampling:**
- "Resample the raster to 100m resolution"
- "Downsample high-resolution imagery to match lower resolution data"
- "Upsample elevation data to higher resolution"

**Mosaicking:**
- "Mosaic multiple Landsat scenes into a single image"
- "Combine multiple DEM tiles into one dataset"
- "Merge satellite imagery from different dates"

**Raster Math:**
- "Calculate NDVI (Normalized Difference Vegetation Index)"
- "Compute slope and aspect from elevation data"
- "Calculate difference between two time periods"

**Zonal Statistics:**
- "Calculate mean elevation for each watershed"
- "Compute maximum temperature per administrative unit"
- "Calculate area-weighted statistics for each polygon"

### 4. Vector Processing

**Spatial Joins:**
- "Join population data to administrative boundaries"
- "Attach elevation values to point locations"
- "Combine attribute data from multiple layers"

**Overlay Operations:**
- "Intersect flood zones with building footprints"
- "Union multiple administrative boundaries"
- "Calculate difference between two polygon layers"

**Geometric Operations:**
- "Calculate area of each polygon"
- "Compute perimeter of administrative boundaries"
- "Measure distance between points"
- "Create convex hulls for point clusters"

**Dissolve and Aggregate:**
- "Dissolve county boundaries to create state boundaries"
- "Aggregate census tracts to zip code level"
- "Combine multiple small polygons into larger units"

### 5. Temporal Analysis

**Time Series:**
- "Analyze land use change from 2010 to 2024"
- "Calculate monthly average temperature trends"
- "Track urban expansion over time"

**Change Detection:**
- "Detect deforestation between two time periods"
- "Identify areas of urban growth"
- "Calculate change in vegetation cover"

**Temporal Aggregation:**
- "Calculate annual average precipitation"
- "Summarize monthly temperature statistics"
- "Aggregate daily data to weekly or monthly"

### 6. Advanced Analysis

**Spatial Clustering:**
- "Identify clusters of high population density"
- "Find hotspots of air pollution"
- "Detect spatial patterns in crime data"

**Interpolation:**
- "Interpolate temperature measurements to create a surface"
- "Create a precipitation map from point observations"
- "Generate a continuous surface from discrete measurements"

**Network Analysis:**
- "Calculate shortest path between two locations"
- "Find all locations within 5km of a road network"
- "Analyze accessibility to services"

**Density Analysis:**
- "Calculate point density for crime incidents"
- "Create kernel density surface for population"
- "Generate heat maps for point data"

### 7. Machine Learning Operations

**Classification:**
- "Classify land use from satellite imagery"
- "Identify building types from aerial imagery"
- "Detect crop types in agricultural fields"

**Object Detection:**
- "Detect buildings in satellite imagery"
- "Identify vehicles in aerial photos"
- "Find ships in ocean imagery"

**Segmentation:**
- "Segment urban areas from rural"
- "Identify individual tree crowns"
- "Segment different land cover types"

### 8. Visualization

**Static Maps:**
- "Create a choropleth map of population density"
- "Generate a map showing elevation with hillshade"
- "Create a map with multiple layers and legend"

**Interactive Maps:**
- "Create an interactive map with Folium"
- "Generate a web map with clickable features"
- "Build a map with time slider for temporal data"

**3D Visualization:**
- "Create a 3D terrain visualization"
- "Generate a 3D building model"
- "Visualize elevation in 3D"

## 🔄 Complete Workflow Examples

### Example 1: Flood Risk Assessment
```
"Assess flood risk for areas within 5km of major rivers in Texas using elevation and precipitation data. Create a risk map and export the results."
```

**Steps:**
1. Search for elevation (DEM) and precipitation data
2. Download datasets
3. Extract areas within 5km buffer of rivers
4. Calculate slope from elevation
5. Overlay with precipitation zones
6. Compute flood risk index
7. Create visualization
8. Export results

### Example 2: Urban Heat Island Analysis
```
"Analyze urban heat islands in New York City. Download land surface temperature data and land cover data, compare temperatures in urban vs rural areas, and create a heat map."
```

**Steps:**
1. Search for LST and land cover data
2. Download datasets
3. Clip to NYC boundaries
4. Reproject to common CRS
5. Extract urban vs rural areas
6. Calculate temperature differences
7. Perform statistical analysis
8. Create visualization
9. Export results

### Example 3: Deforestation Monitoring
```
"Monitor deforestation in the Amazon from 2020 to 2024. Download Landsat imagery for both time periods, classify land cover, detect changes, and create a change map."
```

**Steps:**
1. Search for Landsat imagery (2020 and 2024)
2. Download imagery for both periods
3. Reproject and align datasets
4. Classify land cover for each period
5. Calculate change detection
6. Identify deforested areas
7. Calculate statistics (area, rate of change)
8. Create before/after visualization
9. Export change map and statistics

### Example 4: Population Density Analysis
```
"Analyze population density in California. Download census data, join with administrative boundaries, calculate density per square kilometer, and create a choropleth map."
```

**Steps:**
1. Search for census population data
2. Search for administrative boundaries
3. Download both datasets
4. Spatial join population to boundaries
5. Calculate area of each polygon
6. Compute population density
7. Create choropleth map
8. Export results

## 💡 Tips for Effective Queries

1. **Be Specific:**
   - ✅ "Download Landsat 8 imagery for California from 2023"
   - ❌ "Get some satellite data"

2. **Specify Location:**
   - ✅ "Find elevation data for the Rocky Mountains"
   - ❌ "Get elevation data"

3. **Include Time Period:**
   - ✅ "Download precipitation data for 2020-2024"
   - ❌ "Get weather data"

4. **Mention Data Type:**
   - ✅ "Download vector data for road networks"
   - ❌ "Get some data"

5. **Specify Processing Needs:**
   - ✅ "Clip the data to state boundaries and reproject to UTM"
   - ❌ "Process the data"

## 🎯 Quick Start Examples

Try these simple queries to get started:

1. **Simple Search:**
   ```
   "Show me 5 datasets on flood monitoring"
   ```

2. **Search and Download:**
   ```
   "Find and download OpenStreetMap data for California"
   ```

3. **Search with Processing:**
   ```
   "Find elevation data for Colorado, clip to state boundaries, and create a hillshade map"
   ```

4. **Complete Analysis:**
   ```
   "Analyze land use change in Texas from 2020 to 2024. Download satellite imagery, classify land cover, detect changes, and create a visualization"
   ```

The system will automatically plan and execute the workflow for you!
