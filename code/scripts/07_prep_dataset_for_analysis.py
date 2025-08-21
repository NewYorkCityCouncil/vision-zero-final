#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
from shapely import wkt
import numpy as np 

# In[2]:


# upload

intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')


# #### Preparing Data For Analysis

# In[3]:


# creating version that only includes ever-treated intersections
# excluding intersections that only ever received citywide speed limit reduction
intersection_interventions = ['leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 'street_improvement_corridors_post', 'enhanced_crossing_post']

treated_intersection_ids = intersection_intervention_table.loc[(intersection_intervention_table[intersection_interventions] == 1).any(axis=1), 'intersection_id'].unique()
intersection_intervention_table_ever_treated = intersection_intervention_table[intersection_intervention_table['intersection_id'].isin(treated_intersection_ids)]


# In[4]:


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

# In[5]:


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

# In[12]:


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

# In[28]:


# new dataset with all intersections ever treated between 2015 and 2022, and source column

# 1. LOAD DATA AND DEFINE LISTS
print("Loading data...")
original_df = pd.read_csv('../data/output/intersection_intervention_table_final.csv', low_memory=False)

other_interventions = [
    'leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 
    'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 
    'street_improvement_corridors_post', 'enhanced_crossing_post'
]

# 2. IDENTIFY COHORTS WITH CORRECTED LOGIC
print("Identifying cohorts with corrected logic...")

# --- COHORT A: 'other_interventions' (Restrictive "Clean History" Rule) ---
# This logic remains the same as your original request.
df_long_other = original_df.melt(id_vars=['intersection_id', 'year'], value_vars=other_interventions, var_name='intervention_type', value_name='is_active')
intervention_start_dates = df_long_other[df_long_other['is_active'] == 1].groupby(['intersection_id', 'intervention_type'])['year'].min().reset_index().rename(columns={'year': 'start_year'})
all_ids_with_other_interventions = set(intervention_start_dates['intersection_id'])
ids_to_remove_due_to_outside_treatment = set(intervention_start_dates[~intervention_start_dates['start_year'].between(2015, 2021)]['intersection_id'])
other_interventions_cohort_ids = all_ids_with_other_interventions - ids_to_remove_due_to_outside_treatment

# --- COHORT B: 'speed_limit_only' (CORRECTED DEFINITION) ---
# Must have speed_limit_post=1 at some point, and never have an 'other' intervention.
ids_with_speed_limit = set(original_df[original_df['speed_limit_post'] == 1]['intersection_id'])
# The correct set is those with speed limit MINUS those that also had other treatments.
speed_limit_only_cohort_ids = ids_with_speed_limit - all_ids_with_other_interventions

# 3. COMBINE COHORTS AND BUILD DATAFRAME
final_cohort_ids = other_interventions_cohort_ids.union(speed_limit_only_cohort_ids)
print(f"\nTotal unique intersections in the final dataset: {len(final_cohort_ids):,}")

final_df_all_years = original_df[original_df['intersection_id'].isin(final_cohort_ids)].copy()
final_df_all_years['source'] = np.where(final_df_all_years['intersection_id'].isin(speed_limit_only_cohort_ids), 'speed_limit_only', 'other_interventions')
final_analytic_df = final_df_all_years[final_df_all_years['year'].between(2013, 2023)]

# 4. SAVE THE CORRECTED DATASET
output_path = '../data/output/intersection_intervention_table_with_speed_limit_only_2015-2022.csv'
final_analytic_df.to_csv(output_path, index=False)
print(f"\nSuccessfully created and saved the CORRECTED dataset to: {output_path}")
new_row_count = len(final_analytic_df)
print(f"Total rows in CORRECTED final dataset: {new_row_count:,}")

print("\n--- Validation Results ---")
print(f"Total rows in final dataframe: {len(final_analytic_df):,}")

print("\nBreakdown of total row counts by 'source':")
print(final_analytic_df['source'].value_counts())

# In[29]:


# --- THE COMPLETE UNIVERSE AUDIT SCRIPT ---

print("--- Starting Full Audit of All Kept and Dropped Rows ---")

# 1. LOAD DATA AND DEFINE CONSTANTS
print("\nStep 1: Loading dataframes and defining constants...")
original_df = pd.read_csv('../data/output/intersection_intervention_table_final.csv', low_memory=False)
final_df = pd.read_csv('../data/output/intersection_intervention_table_with_speed_limit_only_2015-2022.csv')

other_interventions = [
    'leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 
    'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 
    'street_improvement_corridors_post', 'enhanced_crossing_post'
]
all_interventions = other_interventions + ['speed_limit_post']

# 2. PARTITION ALL INTERSECTIONS INTO FIVE MUTUALLY EXCLUSIVE GROUPS
print("\nStep 2: Partitioning every intersection into one of five final categories...")

# --- Group 1 & 2: The Intersections that were KEPT ---
ids_kept_other_interventions = set(final_df[final_df['source'] == 'other_interventions']['intersection_id'])
ids_kept_speed_limit_only = set(final_df[final_df['source'] == 'speed_limit_only']['intersection_id'])

# --- Group 3, 4, & 5: The Intersections that were DROPPED ---
original_ids = set(original_df['intersection_id'].unique())
final_ids = set(final_df['intersection_id'].unique())
dropped_ids = original_ids - final_ids

# Dropped Reason C: Never treated with ANY intervention at all.
ever_treated_ids = set(original_df.loc[(original_df[all_interventions] == 1).any(axis=1), 'intersection_id'])
ids_dropped_reason_C = original_ids - ever_treated_ids

# Dropped Reasons A & B: Treated with 'other' but failed the "clean history" rule.
remaining_dropped_ids = dropped_ids - ids_dropped_reason_C
ids_treated_in_window = set(original_df[
    (original_df['year'].between(2015, 2021)) & ((original_df[other_interventions] == 1).any(axis=1))
]['intersection_id'])

ids_dropped_reason_A = {id for id in remaining_dropped_ids if id not in ids_treated_in_window}
ids_dropped_reason_B = {id for id in remaining_dropped_ids if id in ids_treated_in_window}

# --- Report on the partitioning of INTERSECTIONS ---
print("\n--- Breakdown of ALL Intersections by Final Category ---")
print(f"Total Intersections in Universe: {len(original_ids):,}")
print("-" * 55)
print(f"  KEPT: 'other_interventions' (clean history): {len(ids_kept_other_interventions):,}")
print(f"  KEPT: 'speed_limit_only' (correctly defined): {len(ids_kept_speed_limit_only):,}")
print(f"DROPPED A: Treated with 'other' ONLY outside 2015-2021: {len(ids_dropped_reason_A):,}")
print(f"DROPPED B: Treated with 'other' BOTH inside & outside: {len(ids_dropped_reason_B):,}")
print(f"DROPPED C: Never treated with ANY intervention: {len(ids_dropped_reason_C):,}")

# Assert that every intersection has been categorized exactly once
total_categorized_ids = len(ids_kept_other_interventions) + len(ids_kept_speed_limit_only) + \
                        len(ids_dropped_reason_A) + len(ids_dropped_reason_B) + len(ids_dropped_reason_C)
assert len(original_ids) == total_categorized_ids
print("\n(Sanity Check Passed: All intersections are accounted for.)")


# 3. CALCULATE ROW COUNTS (2013-2023) FOR EACH GROUP
print("\nStep 3: Calculating row counts (from 2013-2023) for each category...")

# Filter original data to the relevant analysis window first
original_df_filtered = original_df[original_df['year'].between(2013, 2023)]

# Calculate rows for each of the five groups
rows_kept_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_other_interventions)].shape[0]
rows_kept_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_speed_limit_only)].shape[0]
rows_dropped_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_A)].shape[0]
rows_dropped_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_B)].shape[0]
rows_dropped_C = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_C)].shape[0]

# 4. FINAL RECONCILIATION
print("\nStep 4: Performing final reconciliation of all rows...")

original_filtered_row_count = original_df_filtered.shape[0]
final_row_count = final_df.shape[0]

print("\n--- Full Audit of All Rows (2013-2023) ---")
print(f"Total Rows in Original Data (2013-2023): {original_filtered_row_count:,}")
print("=" * 45)
print(f"  Rows KEPT ('other_interventions'): {rows_kept_A:>12,}")
print(f"  Rows KEPT ('speed_limit_only'): {rows_kept_B:>12,}")
print("-" * 45)
print(f"  Subtotal Kept Rows (Calculated): {rows_kept_A + rows_kept_B:>14,}")
print(f"  Actual Rows in Final File: {final_row_count:>18,}")
print("-" * 45)
print(f"  Rows DROPPED (Reason A): {rows_dropped_A:>18,}")
print(f"  Rows DROPPED (Reason B): {rows_dropped_B:>18,}")
print(f"  Rows DROPPED (Reason C): {rows_dropped_C:>18,}")
print("-" * 45)

total_calculated_rows = rows_kept_A + rows_kept_B + rows_dropped_A + rows_dropped_B + rows_dropped_C
print(f"  GRAND TOTAL (All Categories): {total_calculated_rows:>15,}")

# The ultimate check
try:
    assert (rows_kept_A + rows_kept_B) == final_row_count
    assert total_calculated_rows == original_filtered_row_count
    print("\n✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
    print("AUDIT COMPLETE AND 100% SUCCESSFUL!")
    print("Every row from the 2013-2023 source data has been perfectly accounted for.")
    print("✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
except AssertionError:
    print("\n❌❌❌ VALIDATION FAILED! ❌❌❌")

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
