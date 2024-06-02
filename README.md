# World Map Visualization
This project visualizes a world map as a base map for global distribution visualization. The map includes various geographical features such as countries, continents, oceans, and graticules, making it a comprehensive representation of the world. This base map can be used for further visualization tasks, such as mapping the distribution of specific species, climatic data, or other global phenomena. The map is projected using the Equal Earth projection. The original resource download from https://www.naturalearthdata.com/downloads.

## Features
- Displays country and continent boundaries
- Labels major oceans and continents
- Includes a north arrow and scale bar
- Customizable map elements for clear visualization

## Requirements
- geopandas
- matplotlib
- shapely
- geo_northarrow (https://github.com/pmdscully/geo_northarrow)

## Installation

To install the required Python packages, run:
```bash
pip install geopandas matplotlib shapely
pip install git+https://github.com/pmdscully/geo_northarrow.git
```

## Usage

Download the required shapefiles:

ne_50m_admin_0_countries.shp
ne_50m_graticules_15.shp
ne_50m_wgs84_bounding_box.shp
ne_50m_geography_marine_polys.shp
ne_50m_admin_0_map_subunits.shp
Place the shapefiles in the same directory as the script.

Run the script:

```bash
python geopandas_1.50globalmapViz.py
```

## Limitation
the countrie names were labeled only where the area of the map higer that the average area to avoid the overlapping of information. If the map need the countries' name information, the codes need to be adjusted.