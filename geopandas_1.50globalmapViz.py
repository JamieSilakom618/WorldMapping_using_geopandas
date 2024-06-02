#%%
# Import libraries
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from geo_northarrow import add_north_arrow
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import Point
from shapely.ops import unary_union

# Open the graticule and bounding box
world = gpd.read_file("ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp")
graticule = gpd.read_file("ne_50m_graticules_15/ne_50m_graticules_15.shp")
bbox = gpd.read_file("ne_50m_wgs84_bounding_box/ne_50m_wgs84_bounding_box.shp")
oceans = gpd.read_file("ne_50m_geography_marine_polys/ne_50m_geography_marine_polys.shp")
small_countries = gpd.read_file("ne_50m_admin_0_map_subunits/ne_50m_admin_0_map_subunits.shp")

# Reproject all layers to equal earth
ea_proj = '+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs'
world = world.to_crs(ea_proj)
graticule = graticule.to_crs(ea_proj)
bbox = bbox.to_crs(ea_proj)
oceans = oceans.to_crs(ea_proj)
small_countries = small_countries.to_crs(ea_proj)

# Filter the ocean areas
oceans_filtered = oceans[oceans['featurecla'] == 'ocean']

# Process Pacific Ocean
pacific_names = ["North Pacific Ocean", "South Pacific Ocean"]
pacific_ = oceans_filtered[oceans_filtered["name"].isin(pacific_names)]
pacific_['geometry'] = pacific_['geometry'].apply(lambda geom: geom.buffer(0))
oceans_filtered.at[3, 'geometry'] = unary_union(pacific_['geometry'])

# Process Atlantic Ocean
atlantic_names = ["North Atlantic Ocean", "South Atlantic Ocean"]
atlantic_ = oceans_filtered[oceans_filtered["name"].isin(atlantic_names)]
atlantic_['geometry'] = atlantic_['geometry'].apply(lambda geom: geom.buffer(0))
oceans_filtered.at[2, 'geometry'] = unary_union(atlantic_['geometry'])
oceans_filtered.at[2, 'name'] = oceans_filtered.at[2, 'label'] = "ATLANTIC OCEAN"
oceans_filtered.at[3, 'name'] = oceans_filtered.at[3, 'label'] = "PACIFIC OCEAN"

# Drop unnecessary rows
oceans_filtered = oceans_filtered.drop([4, 6])

# Calculate the 90 percentile of area of countries
average_area = small_countries.geometry.area.quantile(0.5)
# Filter countries with area above average
large_countries = small_countries[small_countries.geometry.area > average_area]

# Get continent area
continents = world.dissolve(by='CONTINENT')

# Create map axis object
my_fig, my_ax = plt.subplots(1, 1, figsize=(26, 20))

# Adjust layout to add more space around the plot
plt.subplots_adjust(top=0.99, bottom=0.12, left=0.05, right=0.95, hspace=2, wspace=0)
my_ax.axis('off')

# Set background color to white
my_ax.set_facecolor('white')
my_fig.patch.set_facecolor('white')

# Add title
my_ax.set_title("Map of the world", fontweight='bold', fontsize=24, pad=5)

# Add bounding box and graticule layers
bbox.plot(ax=my_ax, color='lightblue', linewidth=0)

# Plot the rest of the world
world.plot(ax=my_ax, color="white", linewidth=0.4, linestyle="--", edgecolor='darkgrey')

# Plot the continents with no fill color, only boundaries
continents.plot(ax=my_ax, facecolor='none', edgecolor="black", linestyle='-.', linewidth=0.6)

# Plot the graticule
graticule.plot(ax=my_ax, color='white', linewidth=0.5)

# Plot the oceans
oceans_filtered.plot(ax=my_ax, color='lightblue', linewidth=0.5, edgecolor='blue', alpha=0.6)

# Add country names with small font size, ensuring no duplicates
existed_names = set()
for idx, row in large_countries.iterrows():
    country_name = row["NAME"]
    if country_name not in existed_names:
        my_ax.text(row.geometry.centroid.x, row.geometry.centroid.y, country_name,
                   fontsize=3, ha='center', color='grey')
        existed_names.add(country_name)

# Add continent names in larger font size, excluding "Seven seas (open ocean)"
for idx, row in continents.iterrows():
    if idx != "Seven seas (open ocean)":
        continent_label = row.geometry.centroid
        my_ax.text(continent_label.x, continent_label.y, idx, 
                   fontsize=15, ha='center', color='black', alpha=0.5, weight='bold')

# Add north arrow to the plot
add_north_arrow(my_ax, scale=.35, xlim_pos=.2, ylim_pos=.18, color='#000', text_scaler=3.2, text_yT=-1.25)

# Add graticule labels with degree symbol
for idx, row in graticule.iterrows():
    degree_label = f"{row['degrees']}°"
    line_geom = row.geometry

    if row['direction'] == 'N':  # Latitude lines
        x, y = line_geom.coords[0]  # Start of the line
        my_ax.text(x, y, degree_label, fontsize=7, alpha=0.6, ha='left', va='center', color='blue')
        x_end, y_end = line_geom.coords[-1]
        my_ax.text(x_end, y_end, degree_label, fontsize=7, alpha=0.6, ha='right', va='center', color='blue')
    elif row['direction'] == 'S':  # Latitude lines
        x, y = line_geom.coords[-1]  # End of the line
        my_ax.text(x, y, degree_label, fontsize=7, alpha=0.6, ha='right', va='center', color='blue')
        x_start, y_start = line_geom.coords[0]
        my_ax.text(x_start, y_start, degree_label, fontsize=7, alpha=0.6, ha='left', va='center', color='blue')
    elif row['direction'] == 'E':  # Longitude lines
        x, y = line_geom.coords[-1]  # End of the line
        my_ax.text(x, y, degree_label, fontsize=7, alpha=0.6, ha='left', va='center', color='blue')
        x_start, y_start = line_geom.coords[0]
        my_ax.text(x_start, y_start, degree_label, fontsize=7, alpha=0.6, ha='left', va='center', color='blue')
    elif row['direction'] == 'W':  # Longitude lines
        x, y = line_geom.coords[0]  # Start of the line
        my_ax.text(x, y, degree_label, fontsize=7, alpha=0.6, ha='right', va='center', color='blue')
        x_end, y_end = line_geom.coords[-1]
        my_ax.text(x_end, y_end, degree_label, fontsize=7, alpha=0.6, ha='right', va='center', color='blue')
    else:
        x, y = line_geom.coords[0]  # Start of the line
        my_ax.text(x, y, '0°', fontsize=8, alpha=0.6, ha='right', va='center', color='blue')
        my_ax.text(x, y, '0°', fontsize=8, alpha=0.6, ha='left', va='center', color='blue')

# Label the oceans
for idx, row in oceans_filtered.iterrows():
    name = row['label']
    geo_ = row.geometry 
    if name == "INDIAN OCEAN":
        my_ax.text(geo_.centroid.x, geo_.centroid.y, name,
                   fontsize=16, ha='center', color='blue', alpha=0.3, weight='bold', style='italic')
    elif name == "ATLANTIC OCEAN":
        my_ax.text(geo_.centroid.x, geo_.centroid.y,  name[:8] + "\n" + name[8:],
                   fontsize=16, ha='center', color='blue', alpha=0.3, weight='bold', style='italic')
    elif name == "ARCTIC OCEAN": 
        offset_x = geo_.centroid.x + 3 * 1e6  # Adjust the multiplier to change the offset distance
        offset_y = geo_.centroid.y - 0.3 * 1e6 
        my_ax.text(offset_x, offset_y, name,
                   fontsize=15, ha='center', color='blue', alpha=0.3, weight='bold', style='italic')
    elif name == "PACIFIC OCEAN": 
        offset_x = geo_.centroid.x - 6 * 1e6  # Adjust the multiplier to change the offset distance
        offset_y = geo_.centroid.y - 1 * 1e6 
        my_ax.text(offset_x, offset_y, name[:8] + "\n" + name[8:],
                   fontsize=18, ha='center', color='blue', alpha=0.3, weight='bold', style='italic')
    elif name == "SOUTHERN OCEAN":
        offset_x = geo_.centroid.x + 3 * 1e6  # Adjust the multiplier to change the offset distance
        my_ax.text(offset_x, geo_.centroid.y, name,
                   fontsize=16, ha='center', color='blue', alpha=0.3, weight='bold', style='italic')

# Define the legend elements
legend_elements = [
    Line2D([0], [0], color='black', linestyle='-.', linewidth=2, label='Continental Boundary'),
    Line2D([0], [0], color='darkgrey', linestyle='--', linewidth=2, label='International Boundary'),
    Line2D([0], [0], color='blue', linestyle='-', linewidth=2, label='Maritime Boundary'),
]

info_label = [
    Line2D([0], [0], marker='o', color='w', label='Countries with distribution of $\\it{Genus\ specificepithet}$',
           markerfacecolor='pink', markeredgecolor='black', markersize=20),
    Line2D([0], [0], marker='o', color='w', label='No data available',
           markerfacecolor='white', markeredgecolor='black', markersize=20)
]

# Add the first legend (info_label) to the lower left
legend1 = my_ax.legend(handles=info_label, loc='lower left', bbox_to_anchor=(0.05, -0.1), fontsize=22, frameon=False)
my_ax.add_artist(legend1)

# Add the second legend (legend_elements) to the lower right
legend2 = my_ax.legend(handles=legend_elements, 
                       loc='lower right', 
                       bbox_to_anchor=(0.96, -0.12), 
                       fontsize=14, 
                       title="Legend",
                       title_fontsize='18',
                       frameon=True,      # Enable the frame
                       fancybox=True,     # Enable fancy box (rounded corners)
                       shadow=True)

# Add scale bar
scalebar_length_meters = 2000000  # 2000 km in meters
scalebar_label_left = '0'
scalebar_label_right = f'{scalebar_length_meters / 1000:.0f} km'  # Convert meters to kilometers for the label
scalebar_thickness = 50000
scalebar_x = my_ax.get_xlim()[0] + 0.1 * (my_ax.get_xlim()[1] - my_ax.get_xlim()[0])  # X position
scalebar_y = my_ax.get_ylim()[0] + 0.05 * (my_ax.get_ylim()[1] - my_ax.get_ylim()[0])  # Y position

rect = Rectangle((scalebar_x, scalebar_y), scalebar_length_meters, scalebar_thickness, 
                 linewidth=1, edgecolor='black', facecolor='black', transform=my_ax.transData)
my_ax.add_patch(rect)
my_ax.text(scalebar_x, scalebar_y + scalebar_thickness * 2, scalebar_label_left, 
           ha='center', va='bottom', fontsize=10, color='black')
my_ax.text(scalebar_x + scalebar_length_meters, scalebar_y + scalebar_thickness * 2, scalebar_label_right, 
           ha='center', va='bottom', fontsize=10, color='black')

# Save the figure in high definition
plt.savefig('world_mapv.1.tiff', bbox_inches='tight', dpi=330)

# Show the plot
plt.show()

# %%
