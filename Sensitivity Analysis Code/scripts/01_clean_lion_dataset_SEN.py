#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import geopandas as gpd
from copy import deepcopy
from shapely.ops import unary_union

# In[3]:


# uploading 

# full_dataset, from 00_upload_lion.Rmd file that converts .lyr to .geojson
lion = gpd.read_file('../data/output/lion_geojson/lion.geojson') 
# full_dataset, from DOT as shape file
# lion_shp = gpd.read_file("../data/input/lion_shp/lion.shp") 

# In[4]:


# creating a copy (so don't have to re-upload to get a clean version)

lion_copy = deepcopy(lion)
lion_copy = lion_copy.drop_duplicates()

# In[46]:


# cleaning dataset
# metadata: https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/lion_metadata.pdf

# limiting to only streets, excluding highways, bridges, tunnels, etc.
nyc_streets = lion_copy[lion_copy['RW_TYPE'] == ' 1'] 
# constructed streets only
nyc_streets = nyc_streets[nyc_streets['Status'] == '2'] 
# excludes "generic" street segments that are immaginary
nyc_streets = nyc_streets[(nyc_streets['RB_Layer'].isin(['R', 'B']))] 
# removing highway exits and terminators
nyc_streets = nyc_streets[~(nyc_streets['SegmentTyp'].isin(['E', 'T']))] 

# just the necesary columns
nyc_streets_cleaned = nyc_streets[['PhysicalID', 'SegmentID', 'Street', 'StreetCode', 'LBlockFaceID', 'RBlockFaceID', 'TrafDir', 'BIKE_TRAFDIR', 'StreetWidth_Min', 'StreetWidth_Max', 'Number_Travel_Lanes', 'SegCount', 'POSTED_SPEED', 'SegmentTyp', 'NodeIDFrom', 'NodeIDTo', 'geometry']]
nyc_streets_cleaned = nyc_streets_cleaned.drop_duplicates()

# download
nyc_streets_cleaned.to_file('../data/output/lion_geojson/lion_cleaned.geojson') 

# In[47]:


# # upload cleaned version to avoid re-running code above

# nyc_streets_cleaned = gpd.read_file('../data/output/lion_geojson/lion_cleaned.geojson').drop_duplicates()
# nyc_streets_cleaned = nyc_streets_cleaned.to_crs({'init': 'epsg:2263'}) 

# In[48]:


# creating customized buffer for every street segment

# use average width to fill in missing values
avg_width = nyc_streets_cleaned['StreetWidth_Min'].median()
nyc_streets_cleaned['StreetWidth_Min'] = nyc_streets_cleaned['StreetWidth_Min'].fillna(avg_width)
# creating buffer by cutting street width in half
nyc_streets_cleaned['buffer'] = nyc_streets_cleaned['StreetWidth_Min'] / 2 
nyc_streets_cleaned['buffered_geometry'] = nyc_streets_cleaned.apply(lambda row: row['geometry'].buffer(row['buffer'], cap_style=2), axis=1)
# set as new geometry column
nyc_streets_buffered = gpd.GeoDataFrame(nyc_streets_cleaned, geometry='buffered_geometry', crs='epsg:2263')

# In[49]:


# PhysicalID: an ID associated with a street block
# SegmentID: Multiple segments can comprise a single street block (this results in multiple entries per PhysicalID, each with a unique SegmentID)

# preparing to collapse PhysicalIDs with multiple SegmentIDs into one entry each (so each PhysicalID will represent a single block)
physicalid_counts = nyc_streets_buffered['PhysicalID'].value_counts()
# identify PhysicalIDs with a single SegmentID 
single_segment_ids = physicalid_counts[physicalid_counts == 1].index 
# identify PhysicalIDs with multiple SegmentIDs
multi_segment_ids = physicalid_counts[physicalid_counts > 1].index
# filter the original DataFrame to get streets with single segments 
single_segments = nyc_streets_buffered[nyc_streets_buffered['PhysicalID'].isin(single_segment_ids)] 
# filter the original DataFrame to get streets with multiple segments
multi_segments = nyc_streets_buffered[nyc_streets_buffered['PhysicalID'].isin(multi_segment_ids)] 


# In[50]:


# code to create a single entry for each PhysicalID 
# will collapse geometries for each SegmentID into a single unified street block

def collapse_segments(group):

    # getting the Node IDs for the whole street 
    # the NodeIDFrom of the first segment and the NodeIDTo of the last segment associated with each PhysicalID
    from_nodes = group['NodeIDFrom'].tolist()
    to_nodes = group['NodeIDTo'].tolist()

    # the from node that doesn't intersect with any other segments on the street is the entire segment's from node
    from_node = [i for i in from_nodes if i not in to_nodes]
    # the to node that doesn't intersect with any other segments on the street is the entire segment's to node
    to_node = [i for i in to_nodes if i not in from_nodes]

    # handling edge cases (like traffic circles) where no clear from/to node exists
    if not from_node or not to_node:
        # pick random NodeIDFrom and NodeIDTo pairing 
        random_row = group.sample(1)
        NodeIDFrom = random_row['NodeIDFrom'].values[0]
        NodeIDTo = random_row['NodeIDTo'].values[0]
    else:
        # otherwise extract values from list
        NodeIDFrom = from_node[0]
        NodeIDTo = to_node[0]

    # merge segment geometries and track buffer widths
    combined_geom = unary_union(group['buffered_geometry'])
    buffers = sorted(group['buffer'].tolist())

    # keep a single entry per PhysicalID and replace remaining columns with previously collected values 
    row = group.iloc[0].copy()
    row['NodeIDFrom'] = NodeIDFrom
    row['NodeIDTo'] = NodeIDTo
    row['buffered_geometry'] = combined_geom
    # preserve buffer width variations if they differ
    row['buffer'] = str(buffers) if np.mean(buffers) != buffers[0] else buffers[0]
    
    return row

# process each PhysicalID group that has multiple segments
multi_segments_collapsed = multi_segments.groupby('PhysicalID').apply(collapse_segments).reset_index(drop=True)
# combine with PhysicalIDs that already have one segment per street block
all_segments = pd.concat([single_segments, multi_segments_collapsed])

# download

all_segments.to_csv('../data/output/vz_streets_lion.csv', index=False)

# In[51]:


# compare before and after collapsing

all_segments = gpd.GeoDataFrame(all_segments, geometry='buffered_geometry', crs='epsg:2263') 

id = 183695.0
example = all_segments[all_segments['PhysicalID'] == id]

# uncomment one at a time to view

# # before
# nyc_streets_buffered[nyc_streets_buffered['PhysicalID'] == id].explore()
# after
example.explore()

# In[45]:


# ensuring that abutting streets correctly connect (via NodeIDs)

nodeidfrom = example['NodeIDFrom'].values[0]
nodeidto = example['NodeIDTo'].values[0]

all_segments[(all_segments['NodeIDFrom'] == nodeidfrom) | (all_segments['NodeIDTo'] == nodeidfrom) |
             (all_segments['NodeIDFrom'] == nodeidto) | (all_segments['NodeIDTo'] == nodeidto)].explore()
