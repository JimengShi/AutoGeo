# Common Geospatial Databases and Data Sources

This guide covers major geospatial databases, how to search them, and how to download data using GEOAGENT.

## 🌍 Major Geospatial Data Sources

### 1. **USGS EarthExplorer**
**Website:** https://earthexplorer.usgs.gov/

**Datasets:**
- Landsat (1-9): Satellite imagery from 1972 to present
- MODIS: Moderate Resolution Imaging Spectroradiometer
- ASTER: Advanced Spaceborne Thermal Emission and Reflection Radiometer
- SRTM: Shuttle Radar Topography Mission (elevation)
- NAIP: National Agriculture Imagery Program
- Global Land Survey

**How to Search:**
```
"Search Landsat 8 imagery on USGS EarthExplorer for California 2023"
"Find MODIS data for Amazon rainforest on USGS"
"Download SRTM elevation data from USGS EarthExplorer"
```

**Download Methods:**
- Requires free USGS account
- Can download via web interface or API
- Bulk download available

**GEOAGENT Query Examples:**
- "Search and download Landsat 8 imagery from USGS for California 2023"
- "Get MODIS land surface temperature data from USGS EarthExplorer"
- "Download SRTM elevation data from USGS"

---

### 2. **NASA Earthdata**
**Website:** https://earthdata.nasa.gov/

**Datasets:**
- MODIS products (land, ocean, atmosphere)
- VIIRS: Visible Infrared Imaging Radiometer Suite
- SMAP: Soil Moisture Active Passive
- GRACE: Gravity Recovery and Climate Experiment
- GPM: Global Precipitation Measurement
- Various climate and weather datasets

**How to Search:**
```
"Search MODIS land cover data on NASA Earthdata"
"Find GPM precipitation data from NASA"
"Download VIIRS night lights data from NASA Earthdata"
```

**Download Methods:**
- Free account required
- Direct download or API access
- Some datasets via OPeNDAP

**GEOAGENT Query Examples:**
- "Search and download MODIS vegetation index from NASA Earthdata"
- "Get GPM precipitation data from NASA for 2023"
- "Download VIIRS night lights data from NASA"

---

### 3. **Copernicus Open Access Hub (Sentinel Hub)**
**Website:** https://scihub.copernicus.eu/

**Datasets:**
- Sentinel-1: SAR (Synthetic Aperture Radar) imagery
- Sentinel-2: Multispectral imagery (10m resolution)
- Sentinel-3: Ocean and land color, sea surface temperature
- Sentinel-5P: Atmospheric monitoring

**How to Search:**
```
"Search Sentinel-2 imagery on Copernicus Hub for Amazon 2024"
"Find Sentinel-1 SAR data from Copernicus"
"Download Sentinel-2 data from Copernicus Open Access Hub"
```

**Download Methods:**
- Free account required
- Direct download via web interface
- API access available
- OGC services (WMS, WCS)

**GEOAGENT Query Examples:**
- "Search and download Sentinel-2 imagery from Copernicus for Amazon rainforest 2024"
- "Get Sentinel-1 SAR data from Copernicus Hub for flood monitoring"
- "Download Sentinel-2 data from Copernicus for land use classification"

---

### 4. **OpenStreetMap (OSM)**
**Website:** https://www.openstreetmap.org/

**Datasets:**
- Road networks
- Building footprints
- Points of interest (POIs)
- Administrative boundaries
- Land use polygons
- Water features

**How to Search:**
```
"Download OpenStreetMap road network for California"
"Get building footprints from OpenStreetMap for New York City"
"Extract OSM data for restaurants in Seattle"
```

**Download Methods:**
- Overpass API for queries
- Geofabrik for country/region extracts
- Planet.osm for full database
- OSMnx Python library

**GEOAGENT Query Examples:**
- "Download OpenStreetMap road network for California"
- "Get building footprints from OSM for San Francisco"
- "Extract OSM POI data for hospitals in Texas"

---

### 5. **Natural Earth**
**Website:** https://www.naturalearthdata.com/

**Datasets:**
- Country boundaries
- State/province boundaries
- Coastlines
- Rivers and lakes
- Cultural features (cities, roads)
- Physical features (land, ocean)

**How to Search:**
```
"Download country boundaries from Natural Earth"
"Get state boundaries from Natural Earth for United States"
"Download Natural Earth cultural vector data"
```

**Download Methods:**
- Direct download (no account needed)
- Multiple scales (10m, 50m, 110m)
- Shapefile, GeoJSON formats

**GEOAGENT Query Examples:**
- "Download country boundaries from Natural Earth"
- "Get Natural Earth physical features data"
- "Download Natural Earth cultural vector data at 10m scale"

---

### 6. **NOAA (National Oceanic and Atmospheric Administration)**
**Website:** https://www.noaa.gov/

**Datasets:**
- Climate data (temperature, precipitation)
- Weather data
- Ocean data
- Coastal data
- Satellite imagery
- Hurricane tracks

**How to Search:**
```
"Search NOAA climate data for temperature records"
"Find NOAA precipitation data for United States"
"Download NOAA hurricane track data"
```

**Download Methods:**
- Various portals (NOAA Climate Data, NCEI)
- API access for some datasets
- Direct download

**GEOAGENT Query Examples:**
- "Search and download NOAA temperature data for 2023"
- "Get NOAA precipitation data from NCEI"
- "Download NOAA hurricane track data"

---

### 7. **US Census Bureau**
**Website:** https://www.census.gov/

**Datasets:**
- Population data
- Demographic data
- Census boundaries (tracts, blocks, counties)
- Economic data
- Housing data

**How to Search:**
```
"Download US Census population data for California"
"Get census tract boundaries from US Census Bureau"
"Download demographic data from Census Bureau"
```

**Download Methods:**
- Census API
- TIGER/Line shapefiles
- Direct download

**GEOAGENT Query Examples:**
- "Download US Census population data for New York City"
- "Get census tract boundaries from US Census Bureau"
- "Download demographic data from Census API"

---

### 8. **WorldPop**
**Website:** https://www.worldpop.org/

**Datasets:**
- Population density grids
- Population counts
- Age/sex structures
- Migration data
- Urban growth projections

**How to Search:**
```
"Download WorldPop population density data for Africa"
"Get WorldPop population counts for 2020"
"Download WorldPop data from worldpop.org"
```

**Download Methods:**
- Direct download (no account needed)
- API access
- Multiple resolutions (100m, 1km)

**GEOAGENT Query Examples:**
- "Download WorldPop population density data for Africa 2020"
- "Get WorldPop population counts from worldpop.org"
- "Download WorldPop data at 100m resolution"

---

### 9. **OpenTopography**
**Website:** https://opentopography.org/

**Datasets:**
- LiDAR point clouds
- High-resolution DEMs
- SRTM data
- ASTER GDEM
- Regional elevation datasets

**How to Search:**
```
"Download LiDAR data from OpenTopography for California"
"Get high-resolution DEM from OpenTopography"
"Download SRTM data from OpenTopography"
```

**Download Methods:**
- Free account required
- Direct download
- API access

**GEOAGENT Query Examples:**
- "Download LiDAR data from OpenTopography for urban areas"
- "Get high-resolution DEM from OpenTopography"
- "Download SRTM elevation data from OpenTopography"

---

### 10. **Global Forest Watch**
**Website:** https://www.globalforestwatch.org/

**Datasets:**
- Forest cover
- Tree cover loss/gain
- Deforestation alerts
- Fire alerts
- Land use data

**How to Search:**
```
"Download forest cover data from Global Forest Watch"
"Get tree cover loss data from GFW"
"Download deforestation alerts from Global Forest Watch"
```

**Download Methods:**
- Direct download
- API access
- Map interface

**GEOAGENT Query Examples:**
- "Download forest cover data from Global Forest Watch for Amazon"
- "Get tree cover loss data from GFW for 2020-2024"
- "Download deforestation alerts from Global Forest Watch"

---

### 11. **Dartmouth Flood Observatory**
**Website:** http://floodobservatory.colorado.edu/

**Datasets:**
- Flood extent maps
- Historical flood records
- Flood risk data

**How to Search:**
```
"Download flood extent data from Dartmouth Flood Observatory"
"Get historical flood records from DFO"
"Download flood data from Dartmouth Flood Observatory"
```

**Download Methods:**
- Direct download
- Shapefile format

**GEOAGENT Query Examples:**
- "Download flood extent data from Dartmouth Flood Observatory"
- "Get historical flood records from DFO for major rivers"
- "Download flood data from Dartmouth Flood Observatory"

---

### 12. **HuggingFace Datasets**
**Website:** https://huggingface.co/datasets

**Datasets:**
- Various geospatial datasets
- Preprocessed satellite imagery
- Land use/land cover datasets
- Climate datasets

**How to Search:**
```
"Search geospatial datasets on HuggingFace"
"Find satellite imagery datasets on HuggingFace"
"Download land cover dataset from HuggingFace"
```

**Download Methods:**
- `datasets` Python library
- Direct download
- No account needed for public datasets

**GEOAGENT Query Examples:**
- "Search and download geospatial datasets from HuggingFace"
- "Get satellite imagery dataset from HuggingFace"
- "Download land cover dataset from HuggingFace Hub"

---

## 🔍 How GEOAGENT Searches These Databases

GEOAGENT uses intelligent search that:

1. **Identifies the data source** from your query
2. **Searches the appropriate database** using:
   - Tavily web search for discovery
   - LLM knowledge for specific sources
   - Direct API calls when possible

3. **Downloads data** using:
   - Direct HTTP downloads
   - API clients (when available)
   - Specialized libraries (e.g., `datasets` for HuggingFace)

## 📝 Query Patterns

### Pattern 1: Source-Specific Search
```
"[Source] [Dataset Type] [Location] [Time Period]"

Examples:
- "USGS Landsat 8 imagery California 2023"
- "Copernicus Sentinel-2 data Amazon 2024"
- "NOAA temperature data United States 2023"
```

### Pattern 2: General Search with Source Hint
```
"Search [Dataset Type] from [Source] for [Location]"

Examples:
- "Search elevation data from USGS for Rocky Mountains"
- "Find satellite imagery from Copernicus for Europe"
- "Get population data from WorldPop for Africa"
```

### Pattern 3: Multi-Source Search
```
"Search [Dataset Type] from [Source1] and [Source2]"

Examples:
- "Search elevation data from USGS and OpenTopography"
- "Find satellite imagery from Copernicus and USGS"
```

## 🛠️ Download Methods by Source

| Source | Method | Account Required | API Available |
|--------|--------|------------------|---------------|
| USGS EarthExplorer | Web/API | Yes (free) | Yes |
| NASA Earthdata | Web/API | Yes (free) | Yes |
| Copernicus Hub | Web/API | Yes (free) | Yes |
| OpenStreetMap | Overpass API | No | Yes |
| Natural Earth | Direct | No | No |
| NOAA | Web/API | Sometimes | Yes |
| US Census | API/Web | No | Yes |
| WorldPop | Direct/API | No | Yes |
| OpenTopography | Web/API | Yes (free) | Yes |
| Global Forest Watch | Web/API | No | Yes |
| HuggingFace | Python library | No | Yes |

## 💡 Tips for Effective Queries

1. **Be specific about the source:**
   - ✅ "Download Landsat data from USGS"
   - ❌ "Get some satellite data"

2. **Include location and time:**
   - ✅ "Sentinel-2 imagery for Amazon 2024 from Copernicus"
   - ❌ "Some imagery"

3. **Specify data type:**
   - ✅ "Download elevation data from OpenTopography"
   - ❌ "Get some data"

4. **Use source-specific terminology:**
   - USGS: "Landsat", "MODIS", "SRTM"
   - Copernicus: "Sentinel-1", "Sentinel-2"
   - OSM: "road network", "building footprints", "POIs"

## 🚀 Example Workflows

### Example 1: Multi-Source Data Collection
```
"Search and download Landsat imagery from USGS and Sentinel-2 data from Copernicus for California 2023. Then mosaic and compare them."
```

### Example 2: Complete Analysis Pipeline
```
"Download elevation data from OpenTopography, population data from WorldPop, and administrative boundaries from Natural Earth for Texas. Then create a population density map with elevation overlay."
```

### Example 3: Temporal Analysis
```
"Download MODIS land cover data from NASA Earthdata for Amazon from 2020 to 2024. Analyze deforestation trends and create a change map."
```

## 📚 Additional Resources

- **USGS EarthExplorer Guide:** https://earthexplorer.usgs.gov/
- **NASA Earthdata Guide:** https://www.earthdata.nasa.gov/learn
- **Copernicus User Guide:** https://sentinels.copernicus.eu/web/sentinel/user-guides
- **OpenStreetMap Wiki:** https://wiki.openstreetmap.org/
- **Natural Earth Documentation:** https://www.naturalearthdata.com/downloads/

GEOAGENT can automatically search and download from these sources based on your natural language queries!
