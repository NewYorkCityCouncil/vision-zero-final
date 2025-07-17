#!/usr/bin/env python
# coding: utf-8

# In[468]:


import pandas as pd
import numpy as np
import geopandas as gpd
from copy import deepcopy
from shapely import wkt, unary_union
from geopandas import GeoDataFrame
from shapely.geometry import Point
from shapely.geometry import MultiLineString, LineString

# In[469]:


# uploading tables with collision data for every intersection per year

intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_initial.csv')

# In[470]:


# # removing overlap between intersections and streets in both datasets
# # will make adding interventions easier (interventions in intersections won't be assiged to multiple streets)

# # intersection dataset

# nyc_intersections_vz = pd.read_csv('../data/output/vz_nodes.csv')
# nyc_intersections_vz['street_geom'] = nyc_intersections_vz['street_geom'].apply(wkt.loads)
# nyc_intersections_vz['intersection_geom'] = nyc_intersections_vz['intersection_geom'].apply(wkt.loads)
# nyc_intersections_vz = gpd.GeoDataFrame(nyc_intersections_vz, geometry='intersection_geom', crs='epsg:2263')
# intersections = nyc_intersections_vz.set_geometry('intersection_geom')
# streets = nyc_intersections_vz.set_geometry('street_geom')
# nyc_intersections_vz_trimmed_streets = gpd.overlay(streets, intersections, how='difference')
# nyc_intersections_vz_trimmed_streets['street_geom'] = nyc_intersections_vz_trimmed_streets['street_geom'].apply(lambda geom: wkt.loads(geom.wkt))
# nyc_intersections_vz_trimmed_streets['intersection_geom'] = nyc_intersections_vz_trimmed_streets['intersection_geom'].apply(lambda geom: wkt.loads(geom.wkt))
# nyc_intersections_vz_trimmed_streets = gpd.GeoDataFrame(nyc_intersections_vz_trimmed_streets, geometry='intersection_geom', crs='epsg:2263')
# nyc_intersections_vz_trimmed_streets.to_csv('../data/output/nyc_intersections_vz_trimmed_streets.csv')

# to avoid re-running each time

nyc_intersections_vz_trimmed_streets = pd.read_csv('../data/output/nyc_intersections_vz_trimmed_streets.csv')
nyc_intersections_vz_trimmed_streets['street_geom'] = nyc_intersections_vz_trimmed_streets['street_geom'].apply(wkt.loads)
nyc_intersections_vz_trimmed_streets['intersection_geom'] = nyc_intersections_vz_trimmed_streets['intersection_geom'].apply(wkt.loads)
nyc_intersections_vz_trimmed_streets = gpd.GeoDataFrame(nyc_intersections_vz_trimmed_streets, geometry='intersection_geom', crs='epsg:2263')

# In[361]:


# checking results 

b = gpd.GeoDataFrame(nyc_intersections_vz_trimmed_streets, geometry='street_geom', crs='epsg:2263')
b.loc[:1000].explore()

# ## Adding Interventions

# #### Leading Pedestrian Interval Signals

# - Intersections impacted: intersections containing the intervention

# In[471]:


# uploading leading pedestrian interval signal data

leading_ped_interval_uploaded = gpd.read_file('../data/input/VZV_Leading Pedestrian Interval Signals.geojson')
# leading_ped_interval_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/xc4v-ntf4.csv?$limit=9999999') # code to pull directly from API


# In[472]:


# cleaning leading pedestrian interval signal data

leading_ped_interval_gdf = leading_ped_interval_uploaded.to_crs({'init': 'epsg:2263'}) 
leading_ped_interval_gdf['install_da'] = pd.to_datetime(leading_ped_interval_gdf['install_da'])

# addressing duplicates
leading_ped_interval_gdf = leading_ped_interval_gdf.sort_values('install_da').drop_duplicates(subset=(['install_da','geometry'])) # same place and time (exact duplicates)
leading_ped_interval_gdf = leading_ped_interval_gdf.sort_values('install_da').drop_duplicates(subset=(['geometry']), keep = 'first') # same place, different time (just keeping first occurance)


# In[473]:


# join with intersection dataset

# spatial join to indicate which intersections leading ped intervals land in
leading_ped_interval_merged_w_intersections = gpd.sjoin(leading_ped_interval_gdf, nyc_intersections_vz_trimmed_streets[['intersection_id', 'intersection_geom']]).drop(columns=['index_right'])
# dropping rows without dates (not a very large number)
leading_ped_interval_merged_w_intersections = leading_ped_interval_merged_w_intersections[~leading_ped_interval_merged_w_intersections['install_da'].isnull()]
# drop exact duplicates
leading_ped_interval_merged_w_intersections = leading_ped_interval_merged_w_intersections.drop_duplicates() 
# drop cases where more than one intervention is assigned to single intersection (only keep first instance of any intervention as this location)
leading_ped_interval_merged_w_intersections = leading_ped_interval_merged_w_intersections.sort_values('install_da').drop_duplicates(subset=['intersection_id'], keep='first') 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(leading_ped_interval_merged_w_intersections[['intersection_id', 'install_da']], on='intersection_id', how='left')
# apply the condition to create the 'leading_pedestrian_interval' column
intersection_intervention_table['leading_pedestrian_interval_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['install_da'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['leading_pedestrian_interval_post'] = intersection_intervention_table['leading_pedestrian_interval_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['leading_pedestrian_interval_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['install_da'].dt.year - 2)).astype(int)
# intersection_intervention_table['leading_pedestrian_interval_placebo'] = intersection_intervention_table['leading_pedestrian_interval_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['install_da']) # drop


# In[ ]:


# looking at results

# preparing to limit to just one borough so map isn't as laggy
boroughs = gpd.read_file('../data/input/borough-boundaries.geojson')
# boroughs['geometry'] = boroughs['geometry'].apply(wkt.loads)
boroughs = gpd.GeoDataFrame(boroughs, geometry='geometry', crs='epsg:4326')
boroughs = boroughs.to_crs('epsg:2263')

leading_ped_interval_merged_w_intersections_w_boro = leading_ped_interval_merged_w_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

bx = leading_ped_interval_merged_w_intersections_w_boro[leading_ped_interval_merged_w_intersections_w_boro['boro_name'] == 'Bronx']
bx = gpd.GeoDataFrame(bx, geometry='geometry', crs='epsg:2263')

test = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
m = test[test['intersection_id'].isin(bx['intersection_id'].to_list())].drop(columns=['node_geom', 'street_geom']).explore()
bx.drop(columns=['install_da']).explore(m=m, color='red')

# #### Turn Traffic Calming

# - Intersections impacted: intersections containing the intervention

# In[474]:


# uploading turn traffic calming data

turn_traffic_calming_uploaded = gpd.read_file('../data/input/VZV_Turn Traffic Calming.geojson')
# turn_traffic_calming_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/yfry-tv4r.csv?$limit=9999999') # code to pull directly from API'

# In[475]:


# cleaning turn traffic calming data

turn_traffic_calming_gdf = turn_traffic_calming_uploaded.to_crs({'init': 'epsg:2263'}) 
turn_traffic_calming_gdf['completion'] = pd.to_datetime(turn_traffic_calming_gdf['completion'])

# dropping duplicates
turn_traffic_calming_gdf = turn_traffic_calming_gdf.drop_duplicates(subset=['treatment_','completion','geometry']) # dropping exact duplicates
turn_traffic_calming_gdf = turn_traffic_calming_gdf.drop_duplicates(subset=(['completion','geometry'])) # same time and place, multiple interventions (only keeping one)
turn_traffic_calming_gdf = turn_traffic_calming_gdf.sort_values('completion').drop_duplicates(subset=(['geometry']), keep = 'first') # same place, different time (just keeping first occurance)

# dropping row with no geometry
turn_traffic_calming_gdf = turn_traffic_calming_gdf[turn_traffic_calming_gdf['x'] != '0.0']

# In[476]:


# join with intersection dataset

# spatial join to indicate which intersections turn traffic calming lands in
turn_traffic_calming_merged_w_intersections = gpd.sjoin(turn_traffic_calming_gdf, nyc_intersections_vz_trimmed_streets[['intersection_id', 'intersection_geom']]).drop(columns=['index_right'])
# dropping rows without dates 
turn_traffic_calming_merged_w_intersections = turn_traffic_calming_merged_w_intersections[~turn_traffic_calming_merged_w_intersections['completion'].isnull()]
# drop exact duplicates
turn_traffic_calming_merged_w_intersections = turn_traffic_calming_merged_w_intersections.drop_duplicates() 
# drop cases where more than one intervention is assigned to single intersection (only keep first instance of any intervention as this location)
turn_traffic_calming_merged_w_intersections = turn_traffic_calming_merged_w_intersections.sort_values('completion').drop_duplicates(subset=['intersection_id'], keep='first') 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(turn_traffic_calming_merged_w_intersections[['intersection_id', 'completion']], on='intersection_id', how='left')
# apply the condition to create the 'turn_traffic_calming' column
intersection_intervention_table['turn_traffic_calming_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['completion'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['turn_traffic_calming_post'] = intersection_intervention_table['turn_traffic_calming_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['turn_traffic_calming_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['completion'].dt.year - 2)).astype(int)
# intersection_intervention_table['turn_traffic_calming_placebo'] = intersection_intervention_table['turn_traffic_calming_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['completion']) # drop


# In[ ]:


# looking at results

turn_traffic_calming_merged_w_intersections_w_boro = turn_traffic_calming_merged_w_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

qn = turn_traffic_calming_merged_w_intersections_w_boro[turn_traffic_calming_merged_w_intersections_w_boro['boro_name'] == 'Queens']
qn = gpd.GeoDataFrame(qn, geometry='geometry', crs='epsg:2263')

test = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
m = test[test['intersection_id'].isin(qn['intersection_id'].to_list())].drop(columns=['node_geom', 'street_geom']).explore()
qn.drop(columns=['completion']).explore(m=m, color='red')

# #### 25 MPH Speed Limit 

# - Intersections impacted: Intersections connected to streets impacted by the change (only if traffic flows toward them)

# In[477]:


# uploading speed limit dataset

speed_limits_uploaded = gpd.read_file('../data/input/VZV_Speed Limits.geojson') # downloaded version
# speed_limits_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/978y-cak4.csv?$limit=9999999') # code to pull directly from API

# In[478]:


# cleaning 

speed_limits_gdf = speed_limits_uploaded.to_crs({'init': 'epsg:2263'}) 

# dropping duplicates

speed_limits_gdf = speed_limits_gdf.drop_duplicates()

# finding the midpoint of the streets, will use these geometries to match to street polygons in the VZ dataset
speed_limits_gdf['midpoint'] = speed_limits_gdf['geometry'].apply(lambda line: line.interpolate(0.5, normalized=True))
speed_limits_gdf = speed_limits_gdf.set_geometry('midpoint')

# finding streets that were affected by the default/ 'un-signed' speed limit being lowered to 25 MPH
# update: including all streets with 25 mph, whether signed or not
# unfortunately includes some false positive that were 25 mph before the citywide change (not very many though)
# but if only include signed streets, leave out many that did change, creating many more false negatives
speed_limits_25_gdf = speed_limits_gdf[speed_limits_gdf['postvz_sl'] == '25'] 
# speed_limits_25_gdf = speed_limits_gdf[(speed_limits_gdf['postvz_sl'] == '25') & (speed_limits_gdf['postvz_sg'] == 'NO')]
speed_limits_25_gdf = speed_limits_25_gdf[speed_limits_25_gdf['street'] != 'CONNECTOR'] # removing connectors

# In[479]:


# find streets where intervention happened on

# spatial join to indicate which streets the midpoint land in
speed_limits_merged_w_streets = gpd.sjoin(speed_limits_25_gdf, nyc_intersections_vz_trimmed_streets[['PhysicalID', 'street_geom']].set_geometry('street_geom')).drop(columns=['index_right'])
# list of all streets with intervention
speed_intervention_streets = speed_limits_merged_w_streets['PhysicalID'].unique()

# In[420]:


# # should I drop any that are paired with more than one street? 
# # very small % of all rows (~0.5%)

# t = pd.DataFrame(speed_limits_merged_w_streets.drop_duplicates(subset=['midpoint', 'PhysicalID'])['midpoint'].value_counts())
# t
# len(t[t['count'] >1]) / len(t)

# In[480]:


# finding nodes impacted by the intervention

# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_sl = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(speed_intervention_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_sl = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(speed_intervention_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all affected nodes
sl_intervention_nodes = to_intervention_nodes_sl + from_intervention_nodes_sl

# In[481]:


# join with intersection dataset

# finding these nodes in the intersection df
speed_limit_intervention_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sl_intervention_nodes)]['intersection_id'].to_list()
# 1 if intersection is in the intervention list and the date is after November 7, 2014 (when the speed limit was reduced to 25), 0 if not
intersection_intervention_table['speed_limit_post'] = np.where((intersection_intervention_table['intersection_id'].isin(speed_limit_intervention_intersections)) & (intersection_intervention_table['year'] >= 2014), 1, 0)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['speed_limit_post'] = intersection_intervention_table['speed_limit_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['speed_limit_placebo'] = (intersection_intervention_table['year'] >= (2014 - 2)).astype(int)
# intersection_intervention_table['speed_limit_placebo'] = intersection_intervention_table['speed_limit_placebo'].fillna(0).astype(int)

# In[ ]:


# taking a look at one borough to check work for speed limit streets and intersections

speed_limit_intervention_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sl_intervention_nodes)]
speed_limit_intervention_intersections_w_boro = speed_limit_intervention_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

si = speed_limit_intervention_intersections_w_boro[speed_limit_intervention_intersections_w_boro['boro_name'] == 'Staten Island']
# si['street_geom'] = si['street_geom'].apply(wkt.loads)
si = gpd.GeoDataFrame(si, geometry='street_geom', crs='epsg:2263')

m = si[si['PhysicalID'].isin(speed_intervention_streets)][['PhysicalID', 'NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'street_geom']].drop_duplicates(subset=['street_geom']).explore(color='red')
si = si.set_geometry('intersection_geom')
si[si['NODEID'].isin(sl_intervention_nodes)][['PhysicalID','NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'intersection_geom']].drop_duplicates(subset=['intersection_geom']).explore(m=m, color='blue')


# #### Neighborhood Slow Zones (20 MPH Speed Limit)

# - Intersections impacted: Intersections connected to streets impacted by the change (only if traffic flows toward them, and if they themselves fall into the slow zone)

# In[482]:


# uploading neighborhood slow zones dataset

slow_zones_uploaded = gpd.read_file('../data/input/VZV_Neighborhood Slow Zones.geojson') # downloaded version
# slow_zones_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/8p49-aax2.csv?$limit=9999999') # code to pull directly from API

# In[483]:


# cleaning neighborhood slow zones data

slow_zones_gdf = slow_zones_uploaded.to_crs({'init': 'epsg:2263'}) 
slow_zones_gdf = slow_zones_gdf.rename(columns={'year':'sz_year'})
slow_zones_gdf['sz_year'] = slow_zones_gdf['sz_year'].astype(int)

# finding the midpoint of the streets in the VZ dataset
# will use these point geometries to sjoin to slow_zones_gdf (has polygons for slow zone locations)
nyc_streets_vz_midpoints = deepcopy(nyc_intersections_vz_trimmed_streets)
nyc_streets_vz_midpoints['line_geom'] = nyc_streets_vz_midpoints['line_geom'].apply(wkt.loads)
nyc_streets_vz_midpoints = gpd.GeoDataFrame(nyc_streets_vz_midpoints, geometry='line_geom', crs='epsg:2263')
nyc_streets_vz_midpoints['midpoint'] = nyc_streets_vz_midpoints['line_geom'].apply(lambda line: line.interpolate(0.5, normalized=True))
nyc_streets_vz_midpoints = nyc_streets_vz_midpoints.set_geometry('midpoint')

# In[484]:


# join with streets dataset

# spatial join to indicate which streets the midpoints land in
slow_zones_merged_w_streets = gpd.sjoin(slow_zones_gdf, nyc_streets_vz_midpoints[['PhysicalID', 'midpoint']]).drop(columns=['index_right'])
# adding geometry col
slow_zones_merged_w_streets = slow_zones_merged_w_streets.merge(nyc_intersections_vz_trimmed_streets[['PhysicalID', 'street_geom']], on = 'PhysicalID').rename(columns={'buffered_geometry': 'street_geom', 'geometry': 'zone_geom'})
# drop exact duplicates
slow_zones_merged_w_streets = slow_zones_merged_w_streets.drop_duplicates()
# only keep first instance of an intersection receiving an intervention if it received more than one
slow_zones_merged_w_streets = slow_zones_merged_w_streets.sort_values('sz_year').drop_duplicates(subset=['PhysicalID']) 

# In[485]:


# finding nodes impacted by the intervention

# streets with intervention
slow_zone_streets = slow_zones_merged_w_streets['PhysicalID'].unique()
# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_sz = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(slow_zone_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_sz = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(slow_zone_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all affected nodes
sz_intervention_nodes = to_intervention_nodes_sz + from_intervention_nodes_sz

# In[486]:


# join with intersection dataset

# finding these nodes affected by intersection
slow_zones_merged_w_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sz_intervention_nodes)]
# getting the dates the intervention began
slow_zones_merged_w_intersections = slow_zones_merged_w_intersections.merge(slow_zones_merged_w_streets[['PhysicalID', 'sz_year']], on = 'PhysicalID')
# drop any intersections that fall outside of slow zones
sz_polygon = unary_union(slow_zones_merged_w_streets['zone_geom'])
slow_zones_merged_w_intersections = slow_zones_merged_w_intersections[slow_zones_merged_w_intersections['intersection_geom'].intersects(sz_polygon)]
# drop exact duplicates
slow_zones_merged_w_intersections = slow_zones_merged_w_intersections.drop_duplicates()
# only keep first instance of an intersection receiving an intervention if it received more than one
slow_zones_merged_w_intersections = slow_zones_merged_w_intersections.sort_values('sz_year').drop_duplicates(subset=['intersection_id']) 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(slow_zones_merged_w_intersections[['intersection_id', 'sz_year']], on='intersection_id', how='left')
# apply the condition to create the 'slow_zones' column
intersection_intervention_table['slow_zones_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['sz_year']).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['slow_zones_post'] = intersection_intervention_table['slow_zones_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['slow_zones_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['sz_year'].dt.year - 2)).astype(int)
# intersection_intervention_table['slow_zones_placebo'] = intersection_intervention_table['slow_zones_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['sz_year']) # drop


# In[ ]:


# looking at results

m = slow_zones_merged_w_streets.set_geometry('zone_geom').drop_duplicates(subset=['zone_geom']).drop(columns=['sz_year']).explore(color = 'blue')
n = slow_zones_merged_w_intersections.set_geometry('intersection_geom').drop(columns=['sz_year']).explore(m=m, color='green')
slow_zones_merged_w_intersections.set_geometry('street_geom').drop(columns=['sz_year']).explore(m=n, color='red')

# #### Enhanced Crossings

# - Intersections impacted: Intersections impacted by the intervention AND intersections connected to streets impacted by the intervention (only if traffic flows toward them)

# In[487]:


# uploading enhanced crossings dataset

enhanced_crossings_uploaded = gpd.read_file('../data/input/VZV_Enhanced Crossings- Historical.geojson') # downloaded version
# enhanced_crossings_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/k9a2-vdr8.csv?$limit=9999999') # code to pull directly from API

# In[488]:


# cleaning enhanced crossing data

enhanced_crossings_gdf = enhanced_crossings_uploaded.to_crs({'init': 'epsg:2263'}) 
enhanced_crossings_gdf['date_imple'] = pd.to_datetime(enhanced_crossings_gdf['date_imple'])
enhanced_crossings_gdf = enhanced_crossings_gdf[enhanced_crossings_gdf['date_imple'].notnull()]

# drop cases where same location received multiple interventions (keep first instance)
enhanced_crossings_gdf = enhanced_crossings_gdf.sort_values('date_imple').drop_duplicates(subset=['geometry'], keep='first')

# adding buffer so point accurately captured by street/ intersection polygons
enhanced_crossings_gdf['geometry'] = enhanced_crossings_gdf['geometry'].buffer(1)


# In[489]:


# only including those found in intersections

enhanced_crossings_merged_with_intersections = gpd.sjoin(enhanced_crossings_gdf, nyc_intersections_vz_trimmed_streets[['intersection_id', 'intersection_geom']].set_geometry('intersection_geom'), how='left').drop(columns=['index_right'])
# drop exact duplicates
enhanced_crossings_merged_with_intersections = enhanced_crossings_merged_with_intersections.drop_duplicates()
# saving those not matched with an intersection... must be in the street 
enhanced_crossings_in_streets = enhanced_crossings_merged_with_intersections[enhanced_crossings_merged_with_intersections['intersection_id'].isnull()]

# keep only matched
enhanced_crossings_merged_with_intersections = enhanced_crossings_merged_with_intersections[enhanced_crossings_merged_with_intersections['intersection_id'].notnull()]
# drop cases where more than one intervention is assigned to single location (only keep first instance of any intervention as this location)
enhanced_crossings_merged_with_intersections = enhanced_crossings_merged_with_intersections.sort_values('date_imple').drop_duplicates(subset=['intersection_id']) 


# In[490]:


# dozens still need to be matched, but didn't initially match with an intersection through an .sjoin()
# finding streets these remaining interventions occured in

# merging with streets
enhanced_crossings_merged_with_streets = gpd.sjoin(enhanced_crossings_in_streets.drop(columns=['intersection_id']), nyc_intersections_vz_trimmed_streets[['PhysicalID', 'street_geom']].set_geometry('street_geom'), how='left').drop(columns=['index_right'])
# drop exact duplicates
enhanced_crossings_merged_with_streets = enhanced_crossings_merged_with_streets.drop_duplicates() 

# In[491]:


# some of the points were not matched to anything
# adding buffer to these points to see if they'll get matched 

# matching to intersections

# save points that weren't matched at all in new df
non_matched_enhanced_crossing = enhanced_crossings_merged_with_streets[enhanced_crossings_merged_with_streets['PhysicalID'].isnull()]
non_matched_enhanced_crossing = non_matched_enhanced_crossing.drop(columns=['PhysicalID'])
# drop unmatched points from original dataset
enhanced_crossings_merged_with_streets = enhanced_crossings_merged_with_streets[enhanced_crossings_merged_with_streets['PhysicalID'].notnull()]
# add 15-foot buffer
non_matched_enhanced_crossing = gpd.GeoDataFrame(non_matched_enhanced_crossing, geometry='geometry', crs='epsg:2263')
non_matched_enhanced_crossing['geometry'] = non_matched_enhanced_crossing['geometry'].buffer(15)
# try matching to streets
add_missing_df = non_matched_enhanced_crossing.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left')
add_missing_df = add_missing_df.drop(columns=['index_right'])
add_missing_df = add_missing_df[add_missing_df['PhysicalID'].notnull()] # dropping any that didn't get matched

# merging original with newly found entries
enhanced_crossings_merged_with_streets = pd.concat([enhanced_crossings_merged_with_streets, add_missing_df]).drop(columns=['street_geom'])

# drop exact duplicates
enhanced_crossings_merged_with_streets = enhanced_crossings_merged_with_streets.drop_duplicates() 
# drop cases where more than one intervention is assigned to single intersection (only keep first instance of any intervention as this location)
enhanced_crossings_merged_with_streets = enhanced_crossings_merged_with_streets.sort_values('date_imple').drop_duplicates(subset=['PhysicalID']) 

# In[492]:


# finding nodes impacted by interventions on streets

# streets with intervention
enhanced_crossing_streets = enhanced_crossings_merged_with_streets['PhysicalID'].unique()
# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_ec = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(enhanced_crossing_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_ec = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(enhanced_crossing_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all nodes affected by ECs found in streets
ec_intervention_nodes = set(to_intervention_nodes_ec + from_intervention_nodes_ec) 

# finding nodes affected by the street ECs
street_ec_nodes = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['NODEID'].isin(ec_intervention_nodes))]

# In[493]:


# matching affected intersections to each PhysicalID
enhanced_crossings_merged_with_streets = enhanced_crossings_merged_with_streets.merge(street_ec_nodes[['PhysicalID', 'intersection_id']])
# combining intersections impacted by street ECs and intersections found to have an EC in original .sjoin() with intersection geometry
all_enhanced_crossings_intersections = pd.concat([enhanced_crossings_merged_with_intersections,enhanced_crossings_merged_with_streets.drop(columns=['PhysicalID'])])
all_enhanced_crossings_intersections = all_enhanced_crossings_intersections.drop_duplicates(subset=['intersection_id'])
all_enhanced_crossings_intersections = all_enhanced_crossings_intersections.sort_values('date_imple').drop_duplicates(subset=['geometry'], keep='first')
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(all_enhanced_crossings_intersections[['intersection_id', 'date_imple']], on='intersection_id', how='left')
# apply the condition to create the 'enhanced_crossing' column
intersection_intervention_table['enhanced_crossing_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['date_imple'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['enhanced_crossing_post'] = intersection_intervention_table['enhanced_crossing_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['enhanced_crossing_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['date_imple'].dt.year - 2)).astype(int)
# intersection_intervention_table['enhanced_crossing_placebo'] = intersection_intervention_table['enhanced_crossing_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['date_imple']) # drop

# In[ ]:


# look at results

test = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
m = test[test['intersection_id'].isin(all_enhanced_crossings_intersections['intersection_id'].to_list())].drop(columns=['node_geom','street_geom']).explore(color='green')
# test['street_geom'] = test['street_geom'].apply(wkt.loads)
test = gpd.GeoDataFrame(test, geometry='street_geom', crs='epsg:2263')
n = test[test['PhysicalID'].isin(enhanced_crossings_merged_with_streets['PhysicalID'].to_list())].explore(m=m)
enhanced_crossings_gdf.drop(columns=['date_imple']).explore(m=n, color='red')

# #### 25 MPH Signal Retiming

# - Intersections impacted: Intersections connected to streets impacted by the intervention (only if traffic flows toward them)

# In[502]:


# uploading signal retiming data

# signal_retiming_uploaded = pd.read_csv('../data/input/VZV_Signal Timing_25MPH Signal Retiming.geojson') # downloaded version
signal_retiming_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/d8dp-wfee.csv?$limit=9999999') # code to pull directly from API

# In[503]:


# cleaning signal retiming dataset

# signal_retiming_gdf = signal_retiming_uploaded.to_crs({'init': 'epsg:2263'}) 
signal_retiming_uploaded['the_geom'] = signal_retiming_uploaded['the_geom'].apply(wkt.loads)
signal_retiming_gdf = gpd.GeoDataFrame(signal_retiming_uploaded, geometry='the_geom', crs='epsg:4326')
signal_retiming_gdf = signal_retiming_gdf.to_crs(epsg=2263)

# dropping duplicates
signal_retiming_gdf = signal_retiming_gdf.sort_values('yr').drop_duplicates(subset=['the_geom'], keep='first')

# In[504]:


# with the spped limit dataset the segments were already separated for each street, for this dataset each geometry is a line covering multiple blocks
# have to break up each line into individual street segments before finding midpoints
# first, trim signal retiming corridor lines with intersections

intersections = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
streets = signal_retiming_gdf.set_geometry('the_geom')
signal_retiming_gdf_trimmed_streets = gpd.overlay(streets, intersections, how='difference')

# In[505]:


# get midpoints of all the individual lines within a multilinestring

def get_midpoints(geometry):
    if isinstance(geometry, MultiLineString):
        midpoints = []
        for line in geometry.geoms:
            midpoint = line.interpolate(0.5, normalized=True)
            midpoints.append(midpoint)
        return midpoints
    elif isinstance(geometry, LineString):
        return [geometry.interpolate(0.5, normalized=True)]
    else:
        raise ValueError("Input geometry must be either a LineString or MultiLineString")

# taking the midpoint of every line associated with each signal retiming entry
signal_retiming_gdf_trimmed_streets['midpoint'] = signal_retiming_gdf_trimmed_streets['the_geom'].apply(
    lambda x: get_midpoints(x) if isinstance(x, (MultiLineString, LineString)) else None
)
# signal_retiming_gdf_trimmed_streets['midpoint'] = signal_retiming_gdf_trimmed_streets['the_geom'].apply(lambda x: get_midpoints(x))
# explode list of points
signal_retiming_gdf_trimmed_streets = gpd.GeoDataFrame(signal_retiming_gdf_trimmed_streets.explode('midpoint'), geometry='midpoint', crs='epsg:2263')

# In[506]:


# merging with nyc streets

signal_retiming_merged_w_streets = signal_retiming_gdf_trimmed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left').drop(columns=['index_right'])
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left')

# In[507]:


# some of the points were not matched to street buffers 
# many of these mismatches occur on two-way streets because the point is in the median and doesn't touch either buffer
# adding buffer to points over 3 rounds
# trying to limit the biggest buffers only to points that need it to avoid false positives as much as possible
# not perfect, but probably the best I can get without manually adding streets

# round 1

# save points that weren't matched in new df
missed_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].isnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# drop unmatched points from original dataset
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].notnull()] 
# add 15-foot buffer
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(15)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
signal_retiming_merged_w_streets = pd.concat([signal_retiming_merged_w_streets, add_missing_df])

# round 2

missed_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].isnull()] 
# drop unmatched points from original dataset
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].notnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# add 12-foot buffer (now 27 feet)
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(10)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
signal_retiming_merged_w_streets = pd.concat([signal_retiming_merged_w_streets, add_missing_df])

# round 3

missed_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].isnull()] 
# drop unmatched points from original dataset
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].notnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# add 10-foot buffer (now 37 feet)
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(10)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
signal_retiming_merged_w_streets = pd.concat([signal_retiming_merged_w_streets, add_missing_df])

# interventions matched to a street
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets[signal_retiming_merged_w_streets['PhysicalID'].notnull()]
# only keep first instance of a street receiving and intervention if it received more than one
signal_retiming_merged_w_streets = signal_retiming_merged_w_streets.sort_values('yr').drop_duplicates(subset=['PhysicalID']) 

# In[508]:


# finding nodes impacted by the intervention

# streets with intervention
signal_retiming_streets = signal_retiming_merged_w_streets['PhysicalID'].unique()
# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_sr = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(signal_retiming_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_sr = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(signal_retiming_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all affected nodes
sr_intervention_nodes = to_intervention_nodes_sr + from_intervention_nodes_sr

# In[509]:


# join with intersection dataset

# finding these nodes affected by intersection
signal_retiming_merged_w_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sr_intervention_nodes)]
# getting the dates the intervention began
signal_retiming_merged_w_intersections = signal_retiming_merged_w_intersections.merge(signal_retiming_merged_w_streets[['PhysicalID', 'yr']], on = 'PhysicalID')
# drop exact duplicates
signal_retiming_merged_w_intersections = signal_retiming_merged_w_intersections.drop_duplicates(subset=['intersection_id'])
# only keep first instance of an intersection receiving an intervention if it received more than one
signal_retiming_merged_w_intersections = signal_retiming_merged_w_intersections.sort_values('yr').drop_duplicates(subset=['intersection_id']) 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(signal_retiming_merged_w_intersections[['intersection_id', 'yr']], on='intersection_id', how='left')
# apply the condition to create the 'signal_retiming' column
intersection_intervention_table['signal_retiming_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['yr']).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['signal_retiming_post'] = intersection_intervention_table['signal_retiming_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['signal_retiming_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['yr'].dt.year - 2)).astype(int)
# intersection_intervention_table['signal_retiming_placebo'] = intersection_intervention_table['signal_retiming_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['yr']) # drop


# In[ ]:


# taking a look at one borough to check work 

signal_retiming_intervention_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sr_intervention_nodes)]
signal_retiming_intervention_intersections_w_boro = signal_retiming_intervention_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

bk = signal_retiming_intervention_intersections_w_boro[signal_retiming_intervention_intersections_w_boro['boro_name'] == 'Queens']
bk = gpd.GeoDataFrame(bk, geometry='street_geom', crs='epsg:2263')

m = bk[bk['PhysicalID'].isin(signal_retiming_streets)][['PhysicalID', 'NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'street_geom']].drop_duplicates(subset=['street_geom']).explore(color='red')
bk = bk.set_geometry('intersection_geom')
bk[bk['NODEID'].isin(sr_intervention_nodes)][['PhysicalID','NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'intersection_geom']].drop_duplicates(subset=['intersection_geom']).explore(m=m, color='blue')


# #### Speed Humps

# - Intersections impacted: Intersections connected to streets impacted by the intervention (only if traffic flows toward them)

# In[510]:


# uploading speed bump data

speed_humps_uploaded = gpd.read_file('../data/input/VZV_Speed Humps.geojson') # downloaded version
# speed_humps_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/yjra-caqx.csv?$limit=9999999') # code to pull directly from API

# In[511]:


# cleaning speed bumps dataset

speed_humps_gdf = speed_humps_uploaded.to_crs({'init': 'epsg:2263'}) 

speed_humps_gdf['date_insta'] = pd.to_datetime(speed_humps_gdf['date_insta'])
# keeping first instance of speed bump installation on street
speed_humps_gdf = speed_humps_gdf.sort_values('date_insta').drop_duplicates(subset=(['geometry','on_street','from_stree','to_street']), keep='first') 

# adding speed hump id
speed_humps_gdf.insert(0, 'hump_id', value=range(len(speed_humps_gdf))) # creating ID column

# In[512]:


# trimming lines showing the speed hump corridors with intersections

intersections = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
streets = speed_humps_gdf.set_geometry('geometry')
speed_humps_gdf_trimmed_streets = gpd.overlay(streets, intersections, how='difference')

# In[513]:


# taking the midpoint of every line associated with each speed hump entry
speed_humps_gdf_trimmed_streets['midpoint'] = speed_humps_gdf_trimmed_streets['geometry'].apply(
    lambda x: get_midpoints(x) if isinstance(x, (MultiLineString, LineString)) else None
)
# explode list of points
speed_humps_gdf_trimmed_streets = gpd.GeoDataFrame(speed_humps_gdf_trimmed_streets.explode('midpoint'), geometry='midpoint', crs='epsg:2263')

# In[514]:


# removing hump_ids that have more segments associated with them than total # of humps
# otherwise can't know which segments have humps and which don't

speed_humps_gdf_trimmed_streets['humps'] = speed_humps_gdf_trimmed_streets['humps'].astype(float)
group_by_hump_id = (speed_humps_gdf_trimmed_streets.groupby('hump_id').agg(num_of_segments=('hump_id', 'count'), num_of_humps=('humps', 'mean')))
hump_ids_to_keep = group_by_hump_id[group_by_hump_id['num_of_segments'] <= group_by_hump_id['num_of_humps']].index.to_list()
speed_humps_gdf_trimmed_streets = speed_humps_gdf_trimmed_streets[speed_humps_gdf_trimmed_streets['hump_id'].isin(hump_ids_to_keep)]

# In[515]:


# merging with nyc streets

speed_humps_merged_w_streets = speed_humps_gdf_trimmed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left').drop(columns=['index_right'])
speed_humps_merged_w_streets = speed_humps_merged_w_streets.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left')

# In[516]:


# some of the points were not matched to street buffers 
# many of these mismatches occur on two-way streets because the point is in the median and doesn't touch either buffer
# adding buffer to points that weren't matched
# not perfect, but the best I can do without manually adding streets

# save points that weren't matched in new df
missed_streets = speed_humps_merged_w_streets[speed_humps_merged_w_streets['PhysicalID'].isnull()] 
# drop unmatched points from original dataset
speed_humps_merged_w_streets = speed_humps_merged_w_streets[speed_humps_merged_w_streets['PhysicalID'].notnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# add 15-foot buffer
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(15)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
speed_humps_merged_w_streets = pd.concat([speed_humps_merged_w_streets, add_missing_df])

# In[517]:


# finding nodes impacted by the intervention

# streets with intervention
speed_hump_streets = speed_humps_merged_w_streets['PhysicalID'].unique()
# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_sh = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(speed_hump_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_sh = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(speed_hump_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all affected nodes
sh_intervention_nodes = to_intervention_nodes_sh + from_intervention_nodes_sh

# In[518]:


# join with intersection dataset

# finding these nodes affected by intersection
speed_humps_merged_w_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sh_intervention_nodes)]
# getting the dates the intervention began
speed_humps_merged_w_intersections = speed_humps_merged_w_intersections.merge(speed_humps_merged_w_streets[['PhysicalID', 'date_insta']], on = 'PhysicalID')
# drop exact duplicates
speed_humps_merged_w_intersections = speed_humps_merged_w_intersections.drop_duplicates(subset=['intersection_id'])
# only keep first instance of an intersection receiving an intervention if it received more than one
speed_humps_merged_w_intersections = speed_humps_merged_w_intersections.sort_values('date_insta').drop_duplicates(subset=['intersection_id']) 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(speed_humps_merged_w_intersections[['intersection_id', 'date_insta']], on='intersection_id', how='left')
# apply the condition to create the 'speed_humps' column
intersection_intervention_table['speed_humps_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['date_insta'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['speed_humps_post'] = intersection_intervention_table['speed_humps_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['speed_humps_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['date_insta'].dt.year - 2)).astype(int)
# intersection_intervention_table['speed_humps_placebo'] = intersection_intervention_table['speed_humps_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['date_insta']) # drop


# In[ ]:


# taking a look at one borough to check work 

speed_humps_intervention_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(sh_intervention_nodes)]
speed_humps_intervention_intersections_w_boro = speed_humps_intervention_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

qn = speed_humps_intervention_intersections_w_boro[speed_humps_intervention_intersections_w_boro['boro_name'] == 'Queens']
qn = gpd.GeoDataFrame(qn, geometry='street_geom', crs='epsg:2263')

m = qn[qn['PhysicalID'].isin(speed_hump_streets)][['PhysicalID', 'NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'street_geom']].drop_duplicates(subset=['street_geom']).explore(color='red')
qn = qn.set_geometry('intersection_geom')
qn[qn['NODEID'].isin(sh_intervention_nodes)][['PhysicalID','NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'intersection_geom']].drop_duplicates(subset=['intersection_geom']).explore(m=m, color='blue')


# #### Street Improvement Projects

# - Intersections impacted: Intersections impacted by the intervention

# In[519]:


# uploading SIP intersection data

street_improvement_intersection_uploaded = gpd.read_file('../data/input/VZV_Street Improvement Projects (SIPs) intersections.geojson')
# street_improvement_projects_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/shr7-eqdc.csv?$limit=9999999') # code to pull directly from API


# In[520]:


# cleaning street improvement project data

street_improvement_intersection_gdf = street_improvement_intersection_uploaded.to_crs({'init': 'epsg:2263'}) 
street_improvement_intersection_gdf['end_date'] = pd.to_datetime(street_improvement_intersection_gdf['end_date'])

# In[521]:


# no real evidence of meaningful overlap between datasets

sip = deepcopy(street_improvement_intersection_gdf)
sip['geometry'] = sip['geometry'].buffer(5)

i = deepcopy(turn_traffic_calming_gdf)
i['geometry'] = i['geometry'].buffer(5)
s = sip.sjoin(i)
length = len(s[s['end_date'] == s['completion']])
print(f'Number of SIP intersections installed at same time and place as turn traffic calming: {length}')

i = deepcopy(enhanced_crossings_gdf)
i['geometry'] = i['geometry'].buffer(5)
s = sip.sjoin(i)
length = len(s[s['end_date'] == s['date_imple']])
print(f'Number of SIP intersections installed at same time and place as enhanced crossing: {length}')

i = deepcopy(leading_ped_interval_gdf)
i['geometry'] = i['geometry'].buffer(5)
s = sip.sjoin(i)
length = len(s[s['end_date'] == s['install_da']])
print(f'Number of SIP intersections installed at same time and place as leading pedestrian interval signal: {length}')

# In[522]:


# join with intersection dataset

# spatial join to indicate which intersections leading ped intervals land in
street_improvement_intersection_merged_w_intersections = gpd.sjoin(street_improvement_intersection_gdf, nyc_intersections_vz_trimmed_streets[['intersection_id', 'intersection_geom']]).drop(columns=['index_right'])
# drop exact duplicates
street_improvement_intersection_merged_w_intersections = street_improvement_intersection_merged_w_intersections.drop_duplicates(subset=['intersection_id'])
# only keep first instance of an intersection receiving an intervention if it received more than one
street_improvement_intersection_merged_w_intersections = street_improvement_intersection_merged_w_intersections.sort_values('end_date').drop_duplicates(subset=['intersection_id']) 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(street_improvement_intersection_merged_w_intersections[['intersection_id', 'end_date']], on='intersection_id', how='left')
# apply the condition to create the 'street_improvement_project' column
intersection_intervention_table['street_improvement_project_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['end_date'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['street_improvement_project_post'] = intersection_intervention_table['street_improvement_project_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['street_improvement_project_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['end_date'].dt.year - 2)).astype(int)
# intersection_intervention_table['street_improvement_project_placebo'] = intersection_intervention_table['street_improvement_project_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['end_date']) # drop


# In[ ]:


# checking work

street_improvement_intersection_merged_w_intersections.merge(nyc_intersections_vz_trimmed_streets[['intersection_id', 'intersection_geom']]).drop_duplicates().set_geometry('intersection_geom').explore()

# ### Street Improvement Corridors

# - Intersections impacted: Intersections connected to streets impacted by the intervention (only if traffic flows toward them)

# In[523]:


# uploading SIP corridor data

street_improvement_corridors_uploaded = gpd.read_file('../data/input/VZV_Street Improvement Projects (SIPs) Corridor.geojson')
# street_improvement_corridors_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/2tid-5tcf.csv?$limit=999999')

# In[524]:


# cleaning street improvement corridor data

street_improvement_corridors_gdf = street_improvement_corridors_uploaded.to_crs({'init': 'epsg:2263'}) 
street_improvement_corridors_gdf['end_date'] = pd.to_datetime(street_improvement_corridors_gdf['end_date'])

# In[525]:


# no real evidence of meaningful overlap between datasets

sip = deepcopy(street_improvement_corridors_gdf)
sip['geometry'] = sip['geometry'].buffer(5)

i = deepcopy(speed_humps_gdf)
i['geometry'] = i['geometry'].buffer(5)
s = sip.sjoin(i)
length = len(s[s['end_date'] == s['date_insta']])
print(f'Number of SIP corridors installed at same time and place as speed humps: {length}')

# can only get year level for signal retiming so this is probably an overestimate
i = deepcopy(signal_retiming_gdf)
i['the_geom'] = i['the_geom'].buffer(5)
s = sip.sjoin(i)
length = len(s[s['sip_year'] == s['yr']])
print(f'Number of SIP corridors installed at same time and place as signal retiming: {length}')

# In[526]:


# trimming lines showing the signal retiming corridors with intersections

intersections = nyc_intersections_vz_trimmed_streets.set_geometry('intersection_geom')
streets = street_improvement_corridors_gdf.set_geometry('geometry')
street_improvement_corridors_gdf_trimmed_streets = gpd.overlay(streets, intersections, how='difference')

# In[527]:


# taking the midpoint of every line associated with each speed hump entry
street_improvement_corridors_gdf_trimmed_streets['midpoint'] = street_improvement_corridors_gdf_trimmed_streets['geometry'].apply(
    lambda x: get_midpoints(x) if isinstance(x, (MultiLineString, LineString)) else None
)
# explode list of points
street_improvement_corridors_gdf_trimmed_streets = gpd.GeoDataFrame(street_improvement_corridors_gdf_trimmed_streets.explode('midpoint'), geometry='midpoint', crs='epsg:2263')

# In[528]:


# merging with nyc streets

street_improvement_corridors_merged_w_streets = street_improvement_corridors_gdf_trimmed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left').drop(columns=['index_right'])
street_improvement_corridors_merged_w_streets = street_improvement_corridors_merged_w_streets.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left')


# In[529]:


# some of the points were not matched to street buffers 
# many of these mismatches occur on two-way streets because the point is in the median and doesn't touch either buffer
# adding successively bigger buffers to points over 2 rounds
# trying to limit the biggest buffers only to points that need it to avoid false positives as much as possible

# round 1

# save points that weren't matched in new df
missed_streets = street_improvement_corridors_merged_w_streets[street_improvement_corridors_merged_w_streets['PhysicalID'].isnull()] 
# drop unmatched points from original dataset
street_improvement_corridors_merged_w_streets = street_improvement_corridors_merged_w_streets[street_improvement_corridors_merged_w_streets['PhysicalID'].notnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# add 15-foot buffer
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(15)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
street_improvement_corridors_merged_w_streets = pd.concat([street_improvement_corridors_merged_w_streets, add_missing_df])


# round 2

missed_streets = street_improvement_corridors_merged_w_streets[street_improvement_corridors_merged_w_streets['PhysicalID'].isnull()] 
# drop unmatched points from original dataset
street_improvement_corridors_merged_w_streets = street_improvement_corridors_merged_w_streets[street_improvement_corridors_merged_w_streets['PhysicalID'].notnull()] 
missed_streets = missed_streets.drop(columns=['PhysicalID', 'street_geom'])
# add 12-foot buffer (now 27 feet)
missed_streets['midpoint'] = missed_streets['midpoint'].buffer(10)
# try sjoin again
add_missing_df = missed_streets.sjoin(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']].set_geometry('street_geom'), how = 'left')
add_missing_df = add_missing_df.merge(nyc_intersections_vz_trimmed_streets[['street_geom','PhysicalID']], how = 'left').drop(columns=['index_right'])
# add newly matched points to original dataset
street_improvement_corridors_merged_w_streets = pd.concat([street_improvement_corridors_merged_w_streets, add_missing_df])

# interventions matched to a street
street_improvement_corridors_merged_w_streets = street_improvement_corridors_merged_w_streets[street_improvement_corridors_merged_w_streets['PhysicalID'].notnull()]
# only keep first instance of a street receiving and intervention if it received more than one
street_improvement_corridors_merged_w_streets = street_improvement_corridors_merged_w_streets.sort_values('end_date').drop_duplicates(subset=['PhysicalID']) 

# In[530]:


# finding nodes impacted by the intervention

# streets with intervention
improvement_corridor_streets = street_improvement_corridors_merged_w_streets['PhysicalID'].to_list()
# to-nodes connected to streets with intervention, where traffic travels toward node
to_intervention_nodes_ic = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(improvement_corridor_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['W', 'T']))]['NodeIDTo'].to_list()
# from-nodes connected to streets with intervention, where traffic travels toward node
from_intervention_nodes_ic = nyc_intersections_vz_trimmed_streets[(nyc_intersections_vz_trimmed_streets['PhysicalID'].isin(improvement_corridor_streets)) & (nyc_intersections_vz_trimmed_streets['TrafDir'].isin(['A', 'T']))]['NodeIDFrom'].to_list()
# list of all affected nodes
ic_intervention_nodes = to_intervention_nodes_ic + from_intervention_nodes_ic


# In[531]:


# join with intersection dataset

# finding these nodes affected by intersection
street_improvement_corridors_merged_w_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(ic_intervention_nodes)]
# getting the dates the intervention began
street_improvement_corridors_merged_w_intersections = street_improvement_corridors_merged_w_intersections.merge(street_improvement_corridors_merged_w_streets[['PhysicalID', 'end_date']], on = 'PhysicalID')
# drop exact duplicates
street_improvement_corridors_merged_w_intersections = street_improvement_corridors_merged_w_intersections.drop_duplicates(subset=['intersection_id'])
# only keep first instance of an intersection receiving an intervention if it received more than one
street_improvement_corridors_merged_w_intersections = street_improvement_corridors_merged_w_intersections.sort_values('end_date').drop_duplicates(subset=['intersection_id']) 
# merge the DFs on the intersection_id column
intersection_intervention_table = intersection_intervention_table.merge(street_improvement_corridors_merged_w_intersections[['intersection_id', 'end_date']], on='intersection_id', how='left')
# apply the condition to create the 'street_improvement_corridors' column
intersection_intervention_table['street_improvement_corridors_post'] = (intersection_intervention_table['year'] >= intersection_intervention_table['end_date'].dt.year).astype(int)
# fill NaN values with 0 (for intersection_years that don't have the intervention)
intersection_intervention_table['street_improvement_corridors_post'] = intersection_intervention_table['street_improvement_corridors_post'].fillna(0).astype(int)
# # placebo start date
# intersection_intervention_table['street_improvement_corridors_placebo'] = (intersection_intervention_table['year'] >= (intersection_intervention_table['end_date'].dt.year - 2)).astype(int)
# intersection_intervention_table['street_improvement_corridors_placebo'] = intersection_intervention_table['street_improvement_corridors_placebo'].fillna(0).astype(int)
intersection_intervention_table = intersection_intervention_table.drop(columns=['end_date']) # drop



# In[ ]:


# taking a look at one borough to check work 

street_improvement_corridors_intervention_intersections = nyc_intersections_vz_trimmed_streets[nyc_intersections_vz_trimmed_streets['NODEID'].isin(ic_intervention_nodes)]
street_improvement_corridors_intervention_intersections_w_boro = street_improvement_corridors_intervention_intersections.sjoin(boroughs[['boro_name', 'geometry']], how = 'left')

si = street_improvement_corridors_intervention_intersections_w_boro[street_improvement_corridors_intervention_intersections_w_boro['boro_name'] == 'Staten Island']
si = gpd.GeoDataFrame(si, geometry='street_geom', crs='epsg:2263')

m = si[si['PhysicalID'].isin(improvement_corridor_streets)][['PhysicalID', 'NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'street_geom']].drop_duplicates(subset=['street_geom']).explore(color='red')
si = si.set_geometry('intersection_geom')
si[si['NODEID'].isin(ic_intervention_nodes)][['PhysicalID','NODEID', 'NodeIDFrom', 'NodeIDTo', 'TrafDir', 'intersection_id', 'intersection_geom']].drop_duplicates(subset=['intersection_geom']).explore(m=m, color='blue')


# In[532]:


# when finished, download

intersection_intervention_table.to_csv('../data/output/intersection_intervention_table_w_interventions_added.csv', index=False)

# #### Arterial Slow Zones

# New York City's Arterial Slow Zone program uses a variety of tools to improve safety on high-crash streets, including: 
# - Lower speed limits: The citywide speed limit is 25 mph, unless otherwise posted. 
# - Signal timing changes: These changes are intended to discourage speeding. 
# - Signs: These include distinctive signs to indicate slow zones, and 25 mph signs at major arterial slow zone corridors. 
# - Enforcement: The NYPD enforces the program to prevent traffic fatalities. 
# 
# 
# Pretty much overlaps with other datasets, maybe not worth including
# 

# In[291]:


# uploading arterial slow zones data
# has information on an independent variable

arterial_slow_zones_uploaded = gpd.read_file('../data/input/VZV_Arterial Slow Zones.geojson')
# arterial_slow_zones_uploaded = pd.read_csv('https://data.cityofnewyork.us/resource/hei7-2vf9.csv?$limit=999999')


# In[292]:


# cleaning arterial slow zones data

arterial_slow_zones_gdf = arterial_slow_zones_uploaded.to_crs({'init': 'epsg:2263'}) 
arterial_slow_zones_gdf['enforcemen'] = pd.to_datetime(arterial_slow_zones_gdf['enforcemen'])

# In[293]:


# seems like signal retiming and arterial slow zones completely overlap

a = deepcopy(arterial_slow_zones_gdf)
a['geometry'] = a['geometry'].buffer(5)

i = deepcopy(street_improvement_corridors_gdf)
i['geometry'] = i['geometry'].buffer(5)
s = a.sjoin(i)
length = len(s[s['end_date'] == s['enforcemen']])
print(f'Number of arterial slow zones installed at same time and place as arterial slow zones: {length}')

# overestimation because we can only get them at the year level
i = deepcopy(signal_retiming_gdf)
i['the_geom'] = i['the_geom'].buffer(5)
s = a.sjoin(i)
length = len(s[s['enforcemen'].dt.year == s['yr'].astype(int)])
print(f'Number of arterial slow zones installed at same time and place as signal retiming: {length}')

# In[ ]:


arterial_slow_zones_gdf['id'] = arterial_slow_zones_gdf.index
s = arterial_slow_zones_gdf.sjoin(signal_retiming_gdf)
len(s['id'].unique()) / len(arterial_slow_zones_gdf['id'].unique())

# In[ ]:


# essentially complete overlap with signal retiming

m = arterial_slow_zones_gdf['geometry'].buffer(20).explore(color='red')
signal_retiming_gdf.explore(color='blue', m=m)

# In[ ]:


# essentially complete overlap with citywide speed limit reduction

signed_25mph = speed_limits_gdf[(speed_limits_gdf['postvz_sl'] == '25') & (speed_limits_gdf['postvz_sg'] == 'YES')]
signed_25mph['geometry'] = signed_25mph['geometry'].buffer(20)
m = signed_25mph.set_geometry('geometry').explore(color = 'blue')
arterial_slow_zones_gdf.explore(m=m, color='red')

