#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Chunk 1: Import necessary libraries
import pandas as pd
import geopandas as gpd
from shapely import wkt

# In[2]:


# Chunk 2: Load the datasets
# load the main intersection-year data
intervention_df = pd.read_csv('../data/output/intersection_intervention_table_final.csv')

# load the file containing intersection geometries
geometries_df = pd.read_csv('../data/output/nyc_intersections_vz_trimmed_streets.csv')

print("Intervention data shape:", intervention_df.shape)
print("Geometries data shape:", geometries_df.shape)

# In[3]:


# Chunk 3: Prepare the geometry data for merging
# only need the ID and the geometry column for the merge
intersection_geoms = geometries_df[['intersection_id', 'intersection_geom']].drop_duplicates(subset='intersection_id').copy()

# convert the WKT string to a shapely geometry object
intersection_geoms['intersection_geom'] = intersection_geoms['intersection_geom'].apply(wkt.loads)

print(f"Found {len(intersection_geoms)} unique intersection geometries.")

# In[4]:


# Chunk 4: Merge the geometry data into the main table
# use a left merge to ensure all rows from the original intervention table are kept.
final_df = pd.merge(intervention_df, intersection_geoms, on='intersection_id', how='left')

print("Shape of merged data:", final_df.shape)
final_df.head(3)

# In[5]:


# Chunk 5: Convert to a GeoDataFrame and save to a new file
# promote the pandas DataFrame to a GeoDataFrame
final_gdf = gpd.GeoDataFrame(final_df, geometry='intersection_geom', crs='epsg:2263')

# save the final file
output_path = '../data/output/intersection_intervention_table_final_w_geo.csv'
final_gdf.to_csv(output_path, index=False)

print(f"Successfully saved GeoDataFrame to {output_path}")

# In[6]:


# Chunk 6: Import Folium for mapping
import folium

# In[7]:


# Chunk 7: Prepare data for visualization
# only need one geometry per intersection, not one for each year
# group by the intersection_id and aggregate the data

# sum the injuries over all years for each unique intersection
injury_summary = final_gdf.groupby('intersection_id').agg(
    pedestrian_death_or_injury=('pedestrian_death_or_injury', 'sum'),
    total_death_or_injury=('total_death_or_injury', 'sum'),
    geometry=('intersection_geom', 'first') # The geometry is the same for all years of an intersection
).reset_index()

# convert the aggregated data to a GeoDataFrame
viz_gdf = gpd.GeoDataFrame(injury_summary, geometry='geometry', crs='epsg:2263')

print(f"Created summary for {len(viz_gdf)} unique intersections.")

# In[8]:


# Chunk 8: Create the interactive map
# folium uses a different CRS (EPSG:4326), so we must re-project our data
viz_gdf_4326 = viz_gdf.to_crs('epsg:4326')

# create a base map centered on New York City
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles='CartoDB positron')

# create a GeoJson object to add to the map
# embed the summary statistics into the popup for each intersection
geojson = folium.GeoJson(
    viz_gdf_4326,
    tooltip=folium.GeoJsonTooltip(
        fields=['intersection_id', 'pedestrian_death_or_injury', 'total_death_or_injury'],
        aliases=['Intersection ID:', 'Pedestrian Deaths/Injuries (Total):', 'All Deaths/Injuries (Total):'],
        sticky=True
    ),
    style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1, 'fillOpacity': 0.6}
).add_to(m)


# Display the map in the notebook
m
