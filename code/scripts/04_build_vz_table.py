#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
from shapely import wkt
from geopandas import GeoDataFrame
from itertools import product

# In[2]:


# intersection dataset

nyc_intersections_vz = pd.read_csv('../data/output/collisions-merged-with-intersections.csv')
nyc_intersections_vz['intersection_geom'] = nyc_intersections_vz['intersection_geom'].apply(wkt.loads)
nyc_intersections_vz['street_geom'] = nyc_intersections_vz['street_geom'].apply(wkt.loads)
# nyc_intersections_vz['node_geom'] = nyc_intersections_vz['master_geom'].apply(wkt.loads)
nyc_intersections_vz = gpd.GeoDataFrame(nyc_intersections_vz, geometry='intersection_geom', crs='epsg:2263')

# In[3]:


# creating blank table with a row for each intersection at each year interval 

# create datetime range (span of time that crash data is available)
nyc_intersections_vz['crash_date'] = pd.to_datetime(nyc_intersections_vz['crash_date'], errors='coerce')
start_date = nyc_intersections_vz[nyc_intersections_vz['crash_date'].notnull()]['crash_date'].dt.year.min() 
end_date = nyc_intersections_vz[nyc_intersections_vz['crash_date'].notnull()]['crash_date'].dt.year.max()
vz_dates = list(range(start_date, end_date+1))

# all nyc intersections
nyc_intersections = nyc_intersections_vz['intersection_id'].unique()

# create product of street names and dates using itertools.product
product_ = list(product(nyc_intersections, vz_dates))
intersection_intervention_table = pd.DataFrame()
intersection_intervention_table = intersection_intervention_table.assign(intersection_year = product_)

# also keeping two separate columns
intersection_intervention_table = intersection_intervention_table.assign(intersection_id=intersection_intervention_table['intersection_year'].str.get(0),
                                                                         year=intersection_intervention_table['intersection_year'].str.get(1))

# In[23]:


intersection_intervention_table 

# In[24]:


# creating intersection_year column in dataset to make merging with intersection_intervention_table possible below

# narrowing down to each instance of a collision that led to a death or injury
collisions = nyc_intersections_vz[nyc_intersections_vz['collision_id'].notnull()].drop_duplicates(subset=['collision_id']) 
collisions['year'] = collisions['crash_date'].dt.year
# merging two columns
collisions['intersection_year'] = list(zip(collisions['intersection_id'], collisions['year']))

# In[25]:


# adding outcome columns to vz tables

# intersections
vehicle_collisions_by_year = collisions[['intersection_year', 'collision_id', 'pedestrian_death_or_injury']].groupby('intersection_year').agg({'pedestrian_death_or_injury': 'sum', 'collision_id': 'count'})
vehicle_collisions_by_year = vehicle_collisions_by_year.rename(columns={'collision_id': 'total_death_or_injury'})

# merge datasets using a left merge, creating a table that has crash data for every intersection-year
intersection_intervention_table = intersection_intervention_table.merge(vehicle_collisions_by_year, how='left', on='intersection_year') 
# fill NaN values in the merged columns with 0
intersection_intervention_table['pedestrian_death_or_injury'] = intersection_intervention_table['pedestrian_death_or_injury'].fillna(0) 
intersection_intervention_table['total_death_or_injury'] = intersection_intervention_table['total_death_or_injury'].fillna(0)

# In[26]:


# downloading

intersection_intervention_table.drop(columns=['intersection_year']).to_csv('../data/output/intersection_intervention_table_initial.csv', index=False)

# In[ ]:



