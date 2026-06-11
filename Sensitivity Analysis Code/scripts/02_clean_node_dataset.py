#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import geopandas as gpd
from shapely import wkt

# In[18]:


# uploading node data
# downloaded from: https://www.nyc.gov/content/planning/pages/resources/datasets/lion

nodes = gpd.read_file("../data/input/node/node.shp") 

# In[19]:


# planimetric dataset
# downloaded from: https://data.cityofnewyork.us/Transportation/NYC-Planimetric-Database-Roadbed/xgwd-7vhd
# has polygons for large portion of intersections

nyc_roadbeds_uploaded = pd.read_csv('../data/input/NYC_Planimetric_Database__Roadbed_20240718.csv')
# convert the WKT strings to geometries
nyc_roadbeds_uploaded['the_geom'] = nyc_roadbeds_uploaded['the_geom'].apply(wkt.loads) 
# create a GeoDataFrame
nyc_roadbeds_gdf = gpd.GeoDataFrame(nyc_roadbeds_uploaded, geometry='the_geom') 
# set the initial CRS to WGS84 (EPSG:4326)
nyc_roadbeds_gdf.crs = "EPSG:4326" 
# convert to EPSG:2263 (NAD83 / New York Long Island)
nyc_roadbeds_gdf = nyc_roadbeds_gdf.to_crs("EPSG:2263") 

# In[20]:


# upload the vision zero lion dataset (created in 01_clean_lion_dataset.ipynb)

nyc_streets_vz = pd.read_csv('../data/output/vz_streets_lion.csv')
nyc_streets_vz['buffered_geometry'] = nyc_streets_vz['buffered_geometry'].apply(wkt.loads)
nyc_streets_vz = gpd.GeoDataFrame(nyc_streets_vz, geometry='buffered_geometry', crs='epsg:2263')

# In[21]:


# using sub-code for intersections in the Planimetrics dataset to create df of just intersections
# metadata: https://github.com/CityOfNewYork/nyc-planimetrics/blob/main/Capture_Rules.md

# code for intersections
nyc_intersections = nyc_roadbeds_gdf[nyc_roadbeds_gdf['SUB_CODE'] == 350010] 
# creating unique ID column called intersection_id
nyc_intersections.insert(0, 'intersection_id', value=range(len(nyc_intersections))) 

# In[22]:


# spatial join of node points and planimetric intersection polygons
# finding an intersection-shaped polygon for any nodes that match between the datasets

nodes_w_polygons = nodes.sjoin(nyc_intersections, how = 'left', predicate='intersects').drop(columns=['index_right','SOURCE_ID','SUB_CODE','FEAT_CODE','STATUS','SHAPE_Leng','SHAPE_Area'])
nodes_w_polygons = nodes_w_polygons.merge(nyc_intersections[['intersection_id', 'the_geom']], on='intersection_id', how = 'left').rename(columns={'geometry':'node_geom', 'the_geom':'intersection_geom'})

# In[23]:


# merge on NodeIDFrom or NodeIDTo to find which streets each node is associated with
merge1 = pd.merge(nodes_w_polygons[['NODEID', 'node_geom', 'intersection_id', 'intersection_geom']], nyc_streets_vz[['PhysicalID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'buffer', 'geometry', 'buffered_geometry']], left_on='NODEID', right_on = 'NodeIDFrom', how='left')
merge2 = pd.merge(nodes_w_polygons[['NODEID', 'node_geom', 'intersection_id', 'intersection_geom']], nyc_streets_vz[['PhysicalID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'buffer', 'geometry', 'buffered_geometry']], left_on='NODEID', right_on = 'NodeIDTo', how='left')
nodes_vz = pd.concat([merge1, merge2])
nodes_vz = nodes_vz[nodes_vz['NodeIDTo'].notnull()].rename(columns={'geometry': 'line_geom', 'buffered_geometry':'street_geom'})

# only including nodes that intersect with three or more street polygons (otherwise not actually an intersection)
nodes_vz = nodes_vz.groupby('NODEID').filter(lambda group: len(group['PhysicalID'].value_counts()) >= 3) 


# In[24]:


# checking out the number of streets associated with each node

v = pd.DataFrame(nodes_vz['NODEID'].value_counts())
v 

# In[25]:


# visualizing examples with more than typical number of streets

map = nodes_vz[nodes_vz['NODEID'] == 31690].reset_index().set_geometry('street_geom')
m = map.explore()
map = map.set_geometry('intersection_geom')
n = map.drop_duplicates(subset=['intersection_geom']).explore(m=m, color='green')
map = map.set_geometry('node_geom')
map.drop_duplicates(subset=['node_geom']).explore(m=n, color='red')

# In[26]:


# % of nodes that still need an intersection polygon (weren't matched with a planimetrics polygons)

round((100*len(nodes_vz[nodes_vz['intersection_geom'].isnull()]) / len(nodes_vz)),2)

# In[27]:


# visualizing the nodes that were/ were not matched with intersections

map = nodes_vz.reset_index().loc[0:1000].set_geometry('intersection_geom')
m = map.explore()
map = map.set_geometry('node_geom')
map.explore(m=m, color='red')

# In[29]:


# many remain unmatched (T intersections, for example, are not included in the planimetric dataset)
# will manually create intersections using a default buffer 
# determine the default radius using the average area of all planimetrics intersections
default_buffer = np.sqrt(nyc_intersections['SHAPE_Area'].median() / np.pi)

# filling in empty intersection with node point geometry, then adding a circular buffer with the default radius to the point
nodes_vz['intersection_geom'] = nodes_vz['intersection_geom'].replace('None', np.nan).fillna(nodes_vz['node_geom'])
nodes_vz['intersection_geom'] = nodes_vz.apply(lambda row: row['intersection_geom'].buffer(default_buffer) if pd.isnull(row['intersection_id']) else row['intersection_geom'], axis=1)
nodes_vz = gpd.GeoDataFrame(nodes_vz, geometry='intersection_geom', crs='epsg:2263')

# if an intersection_id is missing (would be missing if node wasn't initially matched), fill in with NODEID
# adding 50,000 so that new IDs don't overlap with any of the existing intersection IDs (range from 0 to 23,991)
nodes_vz['intersection_id'] = nodes_vz['intersection_id'].fillna(nodes_vz['NODEID'] + 50000) 

# In[35]:


# downloading cleaned dataset

nodes_vz.to_csv('../data/output/vz_nodes.csv', index=False)

# In[33]:


# checking out results

test = nodes_vz.reset_index().loc[0:11000]
test = test.set_geometry('street_geom')
m = test.explore()
test = test.set_geometry('intersection_geom')
test.explore(m=m, color='green')


# In[34]:


# zoomed in example

test = nodes_vz.set_geometry('street_geom')
m = test[test['NODEID'].isin([18.0])].explore()
test = test.set_geometry('intersection_geom')
mm = test[test['NODEID'].isin([18.0])].drop_duplicates(subset=['intersection_id']).explore(m=m, color='green')
test = nodes_vz.set_geometry('node_geom')
test[test['NODEID'].isin([18.0])].drop_duplicates(subset=['NODEID']).explore(m=mm, color='red')

# In[49]:


# large intersection covering multiple nodes

test = nodes_vz.set_geometry('intersection_geom')
m = test[nodes_vz['intersection_id'] == 17976].drop_duplicates(subset=['intersection_id']).explore(color='green')
test = test.set_geometry('node_geom')
test[test['intersection_id'] == 17976].drop_duplicates(subset=['NODEID']).explore(m=m, color='red')
