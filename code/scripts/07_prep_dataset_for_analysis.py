#!/usr/bin/env python
# coding: utf-8

# In[104]:


import pandas as pd
import geopandas as gpd
from shapely import wkt

# In[126]:


# upload

intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')


# #### Preparing Data For Analysis

# In[127]:


# creating version that only includes ever-treated intersections
# excluding intersections that only ever received citywide speed limit reduction
intersection_interventions = ['leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 'street_improvement_corridors_post', 'enhanced_crossing_post']

treated_intersection_ids = intersection_intervention_table.loc[(intersection_intervention_table[intersection_interventions] == 1).any(axis=1), 'intersection_id'].unique()
intersection_intervention_table_ever_treated = intersection_intervention_table[intersection_intervention_table['intersection_id'].isin(treated_intersection_ids)]


# In[128]:


# find when each intervention was first introduced to each intersection

# melt the dataframe to create a long format for interventions
df_long = intersection_intervention_table.melt(
    id_vars=["year", "intersection_id"], 
    value_vars=intersection_interventions,
    var_name="intervention", 
    value_name="turned_on"
)

# filter only rows where interventions turned on
df_filtered = df_long[df_long["turned_on"] == 1]

# identify the year each intervention was first turned on for each intersection
intervention_start_dates = df_filtered.groupby(["intersection_id", "intervention"])["year"].min().reset_index()

# In[108]:


# narrow down to set of intersections that only received intervention(s) in 2014, 2015, 2016, or 2017 (4 year period)

# removing any intersections that received an intervention outside the window
outside_intersection_analysis_window = intervention_start_dates[(intervention_start_dates['year'] < 2014) | (intervention_start_dates['year'] > 2017)]
intersection_ids_to_remove = outside_intersection_analysis_window['intersection_id'].unique() 
intersections_inside_treatment_window = intersection_intervention_table_ever_treated[~intersection_intervention_table_ever_treated['intersection_id'].isin(intersection_ids_to_remove)]

# limiting to one year before and 2 years after treatment window
intersection_pre_post_dataset = intersections_inside_treatment_window[(intersections_inside_treatment_window['year'] >= 2013) & (intersections_inside_treatment_window['year'] <= 2019)]

# In[109]:


# # if want to include coordinates

# nodes_vz = pd.read_csv('../data/output/vz_nodes.csv')
# convert = dict(zip(nodes_vz['intersection_id'],nodes_vz['intersection_geom']))

# intersection_pre_post_dataset['intersection_geom'] = intersection_pre_post_dataset['intersection_id'].map(convert)
# intersection_pre_post_dataset['intersection_geom'] = intersection_pre_post_dataset['intersection_geom'].apply(wkt.loads)
# intersection_pre_post_dataset = gpd.GeoDataFrame(intersection_pre_post_dataset, geometry='intersection_geom', crs="EPSG:2263") 
# intersection_pre_post_dataset['centroid'] = intersection_pre_post_dataset['intersection_geom'].centroid

# intersection_pre_post_dataset.drop(columns=['intersection_geom']).to_csv('../data/output/intersection_intervention_table_ever_treated_2014-2018_geocoded.csv', index=False)

# In[110]:


# download
intersection_pre_post_dataset.to_csv('../data/output/intersection_intervention_table_ever_treated_2014-2018.csv', index=False)

# In[111]:


# looking at number of observations for each intervention
# greater number of years

obs_dict = {}
for intervention in intersection_interventions + ['speed_limit_post']:
    obs = len(intersection_pre_post_dataset[intersection_pre_post_dataset[intervention] == 1]['intersection_id'].unique())*7
    obs_dict[intervention] = obs

obs_count_table = pd.DataFrame.from_dict(obs_dict, orient='index', columns=['observations'])
obs_count_table.index.names = ['intervention']
obs_count_table.to_csv('../data/output/observations-by-intervention-type_2014-2018.csv')

obs_count_table

# In[129]:


# using wider range of dates

# narrow down to set of intersections that only received any intervention between 2015-2022 (7 year period)

# removing any intersections that received an intervention outside the window
outside_intersection_analysis_window = intervention_start_dates[(intervention_start_dates['year'] < 2015) | (intervention_start_dates['year'] > 2021)]
intersection_ids_to_remove = outside_intersection_analysis_window['intersection_id'].unique() 
intersections_inside_treatment_window = intersection_intervention_table_ever_treated[~intersection_intervention_table_ever_treated['intersection_id'].isin(intersection_ids_to_remove)]

# limiting to two years before and year after treatment window
intersection_pre_post_dataset_more_years = intersections_inside_treatment_window[(intersections_inside_treatment_window['year'] >= 2013) & (intersections_inside_treatment_window['year'] <= 2023)]

# In[113]:


# # if want to include coordinates

# nodes_vz = pd.read_csv('../data/output/vz_nodes.csv')
# convert = dict(zip(nodes_vz['intersection_id'],nodes_vz['intersection_geom']))

# intersection_pre_post_dataset_more_years['intersection_geom'] = intersection_pre_post_dataset_more_years['intersection_id'].map(convert)
# intersection_pre_post_dataset_more_years['intersection_geom'] = intersection_pre_post_dataset_more_years['intersection_geom'].apply(wkt.loads)
# intersection_pre_post_dataset_more_years = gpd.GeoDataFrame(intersection_pre_post_dataset_more_years, geometry='intersection_geom', crs="EPSG:2263") 
# intersection_pre_post_dataset_more_years['centroid'] = intersection_pre_post_dataset_more_years['intersection_geom'].centroid

# intersection_pre_post_dataset_more_years.drop(columns=['intersection_geom']).to_csv('../data/output/intersection_intervention_table_ever_treated_2015-2022_geocoded.csv', index=False)

# In[130]:


# download
intersection_pre_post_dataset_more_years.to_csv('../data/output/intersection_intervention_table_ever_treated_2015-2022.csv', index=False)

# In[131]:


# looking at number of observations for each intervention

obs_dict = {}
for intervention in intersection_interventions + ['speed_limit_post']:
    obs = len(intersection_pre_post_dataset_more_years[intersection_pre_post_dataset_more_years[intervention] == 1]['intersection_id'].unique())*11
    obs_dict[intervention] = obs

obs_count_table = pd.DataFrame.from_dict(obs_dict, orient='index', columns=['observations'])
obs_count_table.index.names = ['intervention']
obs_count_table.to_csv('../data/output/observations-by-intervention-type_2015-2022.csv')

obs_count_table

# #### Speed Limit Analysis

# Will be used as a robustness checks

# In[132]:


# finding intersections that were only ever treated with the speed limit change

speed_limit_intersection_interventions = intersection_interventions 

# melt the dataframe to create a long format for interventions
df_long_sl = intersection_intervention_table.melt(
    id_vars=["year", "intersection_id"], 
    value_vars=speed_limit_intersection_interventions,
    var_name="intervention", 
    value_name="turned_on"
)

# filter only rows where interventions turned on
df_filtered_sl = df_long_sl[df_long_sl["turned_on"] == 1]

intervention_dict = (
    df_filtered_sl[df_filtered_sl['turned_on'] == 1]
    .groupby('intersection_id')['intervention']
    .unique()
    .apply(list)
    .to_dict()
)

only_speed_limit = {
    inter_id: interventions
    for inter_id, interventions in intervention_dict.items()
    if interventions == ['speed_limit_post']
}

# creating df
speed_limit_intervention_df = intersection_intervention_table[intersection_intervention_table['intersection_id'].isin(only_speed_limit)].drop(columns=intersection_interventions)

# narrow down to 2013-2023 to match other dataset's observation period
speed_limit_intervention_df = speed_limit_intervention_df[(speed_limit_intervention_df['year'] >= 2013) & (speed_limit_intervention_df['year'] <= 2023)]

# download
speed_limit_intervention_df.to_csv('../data/output/speed_limit_intervention_table.csv', index=False)

# In[135]:


# seperate version that combines those only treated with speed limit + the original dataset
# so essentially just a complete ever treated dataset without any exclusions

# creating version that only includes ever-treated intersections
# including intersections that only ever received citywide speed limit reduction
intersection_interventions = ['leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 'street_improvement_corridors_post', 'enhanced_crossing_post', 'speed_limit_post']
treated_intersection_ids = intersection_intervention_table.loc[(intersection_intervention_table[intersection_interventions] == 1).any(axis=1), 'intersection_id'].unique()
intersection_intervention_table_ever_treated = intersection_intervention_table[intersection_intervention_table['intersection_id'].isin(treated_intersection_ids)]

# narrow down to set of intersections that only received any intervention between 2015-2022 + those that only received the speed limit
# removing any intersections that received an intervention outside the window
outside_intersection_analysis_window = intervention_start_dates[(intervention_start_dates['year'] < 2015) | (intervention_start_dates['year'] > 2021)]
outside_intersection_analysis_window = outside_intersection_analysis_window[outside_intersection_analysis_window['intervention'] != 'speed_limit_post']
intersection_ids_to_remove = outside_intersection_analysis_window['intersection_id'].unique() 
intersections_inside_treatment_window = intersection_intervention_table_ever_treated[~intersection_intervention_table_ever_treated['intersection_id'].isin(intersection_ids_to_remove)]

# limiting to two years before and year after treatment window
intersection_pre_post_dataset_w_sl = intersections_inside_treatment_window[(intersections_inside_treatment_window['year'] >= 2013) & (intersections_inside_treatment_window['year'] <= 2023)]

# download
intersection_pre_post_dataset_w_sl.to_csv('../data/output/full_ever_treated_dataset.csv', index=False)
