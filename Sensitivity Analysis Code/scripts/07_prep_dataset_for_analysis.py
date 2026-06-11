#!/usr/bin/env python
# coding: utf-8

# In[2]:


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

# In[6]:


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

# In[7]:


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

# In[8]:


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

# In[9]:


# looking at number of observations for each intervention

obs_dict = {}
for intervention in intersection_interventions + ['speed_limit_post']:
    obs = len(intersection_pre_post_dataset_more_years[intersection_pre_post_dataset_more_years[intervention] == 1]['intersection_id'].unique())*11
    obs_dict[intervention] = obs

obs_count_table = pd.DataFrame.from_dict(obs_dict, orient='index', columns=['observations'])
obs_count_table.index.names = ['intervention']
obs_count_table.to_csv('../data/output/observations-by-intervention-type_2015-2022.csv')

obs_count_table

# In[20]:


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

# In[21]:


import pandas as pd
import numpy as np

# --- 1. LOAD DATA AND DEFINE CONSTANTS ---

print("--- Starting CORRECTED Full Audit of '...with_speed_limit_only...' Dataset ---")
print("\nStep 1: Loading dataframes and defining constants...")

try:
    original_df = pd.read_csv('../data/output/intersection_intervention_table_final.csv', low_memory=False)
    final_df = pd.read_csv('../data/output/intersection_intervention_table_with_speed_limit_only_2015-2022.csv')
except FileNotFoundError as e:
    print(f"\n❌ ERROR: Could not find a required file. Please check the path and filename.")
    print(f"Details: {e}")
    exit()

other_interventions = [
    'leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 
    'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 
    'street_improvement_corridors_post', 'enhanced_crossing_post'
]
all_interventions = other_interventions + ['speed_limit_post']


# --- 2. PARTITION ALL INTERSECTIONS USING CORRECTED, R-ALIGNED LOGIC ---

print("\nStep 2: Partitioning every intersection using the corrected, R-aligned logic...")

# --- Get Ground Truth from the final file ---
ids_kept_other_interventions = set(final_df[final_df['source'] == 'other_interventions']['intersection_id'])
ids_kept_speed_limit_only = set(final_df[final_df['source'] == 'speed_limit_only']['intersection_id'])
final_ids = ids_kept_other_interventions.union(ids_kept_speed_limit_only)

original_ids = set(original_df['intersection_id'].unique())
dropped_ids = original_ids - final_ids

# --- Sub-Partition the DROPPED Intersections ---
# Dropped Reason C: Never treated with ANY intervention at all. (Universal definition)
ever_treated_ids = set(original_df.loc[(original_df[all_interventions] == 1).any(axis=1), 'intersection_id'])
ids_dropped_reason_C = original_ids - ever_treated_ids

# The remaining dropped IDs are those with 'other' treatments who failed the "clean history" rule.
messy_history_dropped_ids = dropped_ids - ids_dropped_reason_C

# #######################################################################################
# # BEGINNING OF THE CORRECTED CODE BLOCK
# # This section replaces the previous faulty A/B split logic.
# #######################################################################################

# First, get the start year for every single intervention instance
df_long = original_df.melt(
    id_vars=['intersection_id', 'year'],
    value_vars=other_interventions,
    var_name='intervention_type',
    value_name='is_active'
)
intervention_start_dates = df_long[df_long['is_active'] == 1].groupby(
    ['intersection_id', 'intervention_type']
)['year'].min().reset_index().rename(columns={'year': 'start_year'})

# Next, for each intersection, create the two boolean flags, just like in R
cohort_flags = intervention_start_dates.groupby('intersection_id')['start_year'].agg([
    ('treated_inside_window', lambda s: s.between(2015, 2021).any()),
    ('treated_outside_window', lambda s: (~s.between(2015, 2021)).any())
]).reset_index()

# Filter these flags to only the intersections that were actually DROPPED for a messy history
dropped_cohort_flags = cohort_flags[cohort_flags['intersection_id'].isin(messy_history_dropped_ids)]

# Now, use boolean masks to create the final ID sets for the dropped reasons A & B
outside_only_mask = (~dropped_cohort_flags['treated_inside_window']) & (dropped_cohort_flags['treated_outside_window'])
ids_dropped_reason_A = set(dropped_cohort_flags[outside_only_mask]['intersection_id'])

mixed_mask = (dropped_cohort_flags['treated_inside_window']) & (dropped_cohort_flags['treated_outside_window'])
ids_dropped_reason_B = set(dropped_cohort_flags[mixed_mask]['intersection_id'])

# #######################################################################################
# # END OF THE CORRECTED CODE BLOCK
# #######################################################################################


# --- Report on the partitioning of INTERSECTIONS ---
print("\n--- Breakdown of ALL Intersections by Final Category (Corrected Logic) ---")
print(f"Total Intersections in Universe: {len(original_ids):,}")
print("-" * 65)
print(f"  KEPT: 'other_interventions' (clean history): {len(ids_kept_other_interventions):,}")
print(f"  KEPT: 'speed_limit_only' cohort (impure): {len(ids_kept_speed_limit_only):,}")
print(f"DROPPED A: Treated with 'other' ONLY outside 2015-2021: {len(ids_dropped_reason_A):,}")
print(f"DROPPED B: Treated with 'other' BOTH inside & outside: {len(ids_dropped_reason_B):,}")
print(f"DROPPED C: Never treated with ANY intervention: {len(ids_dropped_reason_C):,}")

total_categorized_ids = len(ids_kept_other_interventions) + len(ids_kept_speed_limit_only) + \
                        len(ids_dropped_reason_A) + len(ids_dropped_reason_B) + len(ids_dropped_reason_C)
assert len(original_ids) == total_categorized_ids
print("\n(Sanity Check Passed: All intersections are accounted for.)")


# --- 3. CALCULATE AND RECONCILE ROW COUNTS ---
print("\nStep 3: Calculating row counts (from 2013-2023) for each category...")

original_df_filtered = original_df[original_df['year'].between(2013, 2023)]
final_row_count = final_df.shape[0]

rows_kept_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_other_interventions)].shape[0]
rows_kept_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_speed_limit_only)].shape[0]
rows_dropped_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_A)].shape[0]
rows_dropped_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_B)].shape[0]
rows_dropped_C = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_reason_C)].shape[0]


# --- 4. FINAL RECONCILIATION ---
print("\nStep 4: Performing final reconciliation of all rows...")

print("\n--- Full Audit of All Rows (2013-2023) ---")
print(f"Total Rows in Original Data (2013-2023): {original_df_filtered.shape[0]:,}")
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

try:
    assert (rows_kept_A + rows_kept_B) == final_row_count
    assert total_calculated_rows == original_df_filtered.shape[0]
    print("\n✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
    print("CORRECTED AUDIT COMPLETE AND 100% SUCCESSFUL!")
    print("Every row has been perfectly accounted for using the corrected logic.")
    print("✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
except AssertionError:
    print("\n❌❌❌ VALIDATION FAILED! The row counts do not reconcile. ❌❌❌")

# In[5]:


# using wider range of dates (2013-2023)

# narrow down to set of intersections that only received any intervention between 2013-2023 (10 year period)

# removing any intersections that received an intervention outside the window
outside_intersection_analysis_window = intervention_start_dates[(intervention_start_dates['year'] < 2013) | (intervention_start_dates['year'] > 2023)]
intersection_ids_to_remove = outside_intersection_analysis_window['intersection_id'].unique() 
intersections_inside_treatment_window = intersection_intervention_table_ever_treated[~intersection_intervention_table_ever_treated['intersection_id'].isin(intersection_ids_to_remove)]

# limiting to just 2013-2023
intersection_pre_post_dataset_even_more_years = intersections_inside_treatment_window[(intersections_inside_treatment_window['year'] >= 2013) & (intersections_inside_treatment_window['year'] <= 2023)]

# In[6]:


# Ensure the DataFrame is a copy to prevent SettingWithCopyWarning
intersection_pre_post_dataset_even_more_years = intersection_pre_post_dataset_even_more_years.copy()

print("--- Adding 'early' and 'late' adopter flags ---")

# --- Step 1: Identify the set of intersection IDs for each flag ---

# For 'early': Find all unique intersection IDs that had ANY treatment start in 2013 or 2014.
early_ids = set(
    intervention_start_dates[
        intervention_start_dates['year'].isin([2013, 2014])
    ]['intersection_id'].unique()
)

# For 'late': First, find the single FIRST-EVER treatment year for each intersection.
first_ever_treatment_year = intervention_start_dates.groupby('intersection_id')['year'].min()

# Now, identify the intersection IDs where this first-ever year was 2022 or 2023.
late_ids = set(
    first_ever_treatment_year[
        first_ever_treatment_year.isin([2022, 2023])
    ].index
)

# --- Step 2: Create the new columns using the efficient .isin() method ---
# This checks if each row's intersection_id is in our pre-calculated sets.
# .astype(int) cleanly converts the boolean result (True/False) to binary (1/0).

intersection_pre_post_dataset_even_more_years['early'] = intersection_pre_post_dataset_even_more_years['intersection_id'].isin(early_ids).astype(int)
intersection_pre_post_dataset_even_more_years['late'] = intersection_pre_post_dataset_even_more_years['intersection_id'].isin(late_ids).astype(int)


# --- Step 3 (Optional but Recommended): Validate the results ---

print("\n--- Validation ---")
num_early_intersections = len(early_ids)
num_late_intersections = len(late_ids)

print(f"Identified {num_early_intersections:,} unique intersections for the 'early' flag.")
print(f"Identified {num_late_intersections:,} unique intersections for the 'late' flag.")

print("\nValue counts for the 'early' flag in the final dataframe:")
# Multiplying by 11 years (2013-2023) should approximate the row count
print(intersection_pre_post_dataset_even_more_years['early'].value_counts()) 

print("\nValue counts for the 'late' flag in the final dataframe:")
print(intersection_pre_post_dataset_even_more_years['late'].value_counts())

print("\nFirst 5 rows of the dataframe with new columns:")
print(intersection_pre_post_dataset_even_more_years[['intersection_id', 'year', 'early', 'late']].head())

# To see a random sample of 10 rows where 'late' is 1:
# print("\nSample of 'late' adopter rows:")
# print(intersection_pre_post_dataset_even_more_years[intersection_pre_post_dataset_even_more_years['late'] == 1].sample(10)[['intersection_id', 'year', 'early', 'late']])

# In[ ]:


print("\n--- Performing rigorous validation on 'early' and 'late' flags ---")

# --- Step 1: Create a "clean" history table for validation ---
# Get the set of intersection IDs that are ACTUALLY in the final dataset.
final_ids = set(intersection_pre_post_dataset_even_more_years['intersection_id'].unique())

# Filter the master start date list to only include these final intersections.
# All our checks will be against this clean history.
clean_intervention_start_dates = intervention_start_dates[
    intervention_start_dates['intersection_id'].isin(final_ids)
]

# --- Step 2: Validation for the 'early' flag ---
print("\nValidating 'early' flag...")

# Ground Truth: From the clean history, which IDs SHOULD be flagged as early?
ground_truth_early_ids = set(
    clean_intervention_start_dates[
        clean_intervention_start_dates['year'].isin([2013, 2014])
    ]['intersection_id'].unique()
)

# Test Set: Which IDs were ACTUALLY flagged as early in the dataframe?
flagged_early_ids = set(
    intersection_pre_post_dataset_even_more_years[
        intersection_pre_post_dataset_even_more_years['early'] == 1
    ]['intersection_id'].unique()
)

# The Check: Compare the sets.
if ground_truth_early_ids == flagged_early_ids:
    print("✅ Validation PASSED for 'early' flag.")
else:
    print("❌ VALIDATION FAILED for 'early' flag!")
    mismatch = ground_truth_early_ids.symmetric_difference(flagged_early_ids)
    print(f"   Found {len(mismatch)} mismatched intersection(s).")
    print(f"   Example mismatched ID: {list(mismatch)[0]}")


# --- Step 3: Validation for the 'late' flag ---
print("\nValidating 'late' flag...")

# Test Set: Which IDs were ACTUALLY flagged as late in the dataframe?
flagged_late_ids = set(
    intersection_pre_post_dataset_even_more_years[
        intersection_pre_post_dataset_even_more_years['late'] == 1
    ]['intersection_id'].unique()
)

# The Check: For this flagged group, did any of them have a treatment starting BEFORE 2022?
late_intersections_history = clean_intervention_start_dates[
    clean_intervention_start_dates['intersection_id'].isin(flagged_late_ids)
]

# Find the first-ever treatment year for each of these intersections.
first_treatment_for_late_group = late_intersections_history.groupby('intersection_id')['year'].min()

# Find any intersections that violate the rule (first treatment < 2022).
violators = first_treatment_for_late_group[first_treatment_for_late_group < 2022]

if violators.empty:
    print("✅ Validation PASSED for 'late' flag: All flagged intersections have no treatments starting before 2022.")
else:
    print("❌ VALIDATION FAILED for 'late' flag!")
    print(f"   Found {len(violators)} intersection(s) flagged as 'late' that had treatments before 2022.")
    print(f"   Example violating ID and its first treatment year:")
    print(violators.head(1))

# In[10]:


# download

intersection_pre_post_dataset_even_more_years.to_csv('../data/output/intersection_intervention_table_ever_treated_2013-2023.csv', index=False)

# In[11]:


import pandas as pd
import numpy as np

# --- 1. SETUP: LOAD DATA AND DEFINE CONSTANTS ---

print("--- Starting FINAL CORRECTED Full Audit of the 'Ever Treated 2013-2023' Dataset ---")
print("\nStep 1: Loading dataframes and defining constants...")

try:
    original_df = pd.read_csv('../data/output/intersection_intervention_table_final.csv', low_memory=False)
    final_df = pd.read_csv('../data/output/intersection_intervention_table_ever_treated_2013-2023.csv')
except FileNotFoundError as e:
    print(f"\n❌ ERROR: Could not find a required file. Please check the path and filename.")
    print(f"Details: {e}")
    exit()

other_interventions = [
    'leading_pedestrian_interval_post', 'turn_traffic_calming_post', 'slow_zones_post', 
    'signal_retiming_post', 'speed_humps_post', 'street_improvement_project_post', 
    'street_improvement_corridors_post', 'enhanced_crossing_post'
]
all_interventions = other_interventions + ['speed_limit_post']


# --- 2. PARTITION ALL INTERSECTIONS USING CORRECTED, R-ALIGNED LOGIC ---

print("\nStep 2: Partitioning every intersection using the correct, R-aligned logic...")

original_ids = set(original_df['intersection_id'].unique())
kept_ids = set(final_df['intersection_id'].unique())
dropped_ids = original_ids - kept_ids

# --- Sub-Partition the DROPPED Intersections (This part remains the same) ---
ever_treated_ids = set(original_df.loc[(original_df[all_interventions] == 1).any(axis=1), 'intersection_id'])
ids_dropped_never_treated = original_ids - ever_treated_ids

all_ids_with_other_interventions = set(original_df.loc[(original_df[other_interventions] == 1).any(axis=1), 'intersection_id'])
ids_with_speed_limit = set(original_df[original_df['speed_limit_post'] == 1]['intersection_id'])
ids_dropped_speed_limit_only = ids_with_speed_limit - all_ids_with_other_interventions

ids_dropped_contaminated = dropped_ids - ids_dropped_never_treated - ids_dropped_speed_limit_only

# #######################################################################################
# # BEGINNING OF THE CORRECTED CODE BLOCK
# # This entire section replaces the previous faulty logic.
# #######################################################################################

# --- Sub-Partition the KEPT Intersections (using direct R logic translation) ---

# First, get the start year for every single intervention instance
df_long = original_df.melt(
    id_vars=['intersection_id', 'year'],
    value_vars=other_interventions,
    var_name='intervention_type',
    value_name='is_active'
)
intervention_start_dates = df_long[df_long['is_active'] == 1].groupby(
    ['intersection_id', 'intervention_type']
)['year'].min().reset_index().rename(columns={'year': 'start_year'})

# Next, for each intersection, create the two boolean flags, just like in R
cohort_flags = intervention_start_dates.groupby('intersection_id')['start_year'].agg([
    ('treated_inside_window', lambda s: s.between(2015, 2021).any()),
    ('treated_outside_window', lambda s: (~s.between(2015, 2021)).any())
]).reset_index()

# Filter these flags to only the intersections that were actually KEPT in the final dataset
kept_cohort_flags = cohort_flags[cohort_flags['intersection_id'].isin(kept_ids)]

# Now, use boolean masks to create the final ID sets, mimicking the R 'case_when'
middle_only_mask = (kept_cohort_flags['treated_inside_window']) & (~kept_cohort_flags['treated_outside_window'])
ids_kept_clean_2015_2021 = set(kept_cohort_flags[middle_only_mask]['intersection_id'])

outside_only_mask = (~kept_cohort_flags['treated_inside_window']) & (kept_cohort_flags['treated_outside_window'])
ids_kept_clean_outside = set(kept_cohort_flags[outside_only_mask]['intersection_id'])

mixed_mask = (kept_cohort_flags['treated_inside_window']) & (kept_cohort_flags['treated_outside_window'])
ids_kept_mixed_history = set(kept_cohort_flags[mixed_mask]['intersection_id'])

# #######################################################################################
# # END OF THE CORRECTED CODE BLOCK
# #######################################################################################


# --- Report on the partitioning of INTERSECTIONS ---
print("\n--- Breakdown of ALL Intersections by Final Category (Corrected Logic) ---")
print(f"Total Intersections in Universe: {len(original_ids):,}")
print("-" * 75)
print("KEPT INTERSECTIONS (in this dataset):")
print(f"  - Clean History (All 'other' treatments 2015-2021 Only): {len(ids_kept_clean_2015_2021):,}")
print(f"  - Mixed History (Treated BOTH inside & outside 2015-2021): {len(ids_kept_mixed_history):,}")
print(f"  - Clean History (Treated ONLY outside 2015-2021): {len(ids_kept_clean_outside):,}")
print("DROPPED INTERSECTIONS (from this dataset):")
print(f"  - Dropped: Contaminated History (treatment <2013 or >2023): {len(ids_dropped_contaminated):,}")
print(f"  - Dropped: Only ever received 'speed_limit_post': {len(ids_dropped_speed_limit_only):,}")
print(f"  - Dropped: Never treated with any intervention: {len(ids_dropped_never_treated):,}")

total_categorized_ids = len(ids_kept_clean_2015_2021) + len(ids_kept_mixed_history) + len(ids_kept_clean_outside) + \
                        len(ids_dropped_contaminated) + len(ids_dropped_speed_limit_only) + len(ids_dropped_never_treated)
assert len(original_ids) == total_categorized_ids
print("\n(Sanity Check Passed: All intersections are accounted for.)")


# --- 3. CALCULATE AND RECONCILE ROW COUNTS (2013-2023) ---
print("\nStep 3: Calculating and reconciling row counts (from 2013-2023)...")

original_df_filtered = original_df[original_df['year'].between(2013, 2023)]
final_row_count = final_df.shape[0]

rows_kept_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_clean_2015_2021)].shape[0]
rows_kept_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_mixed_history)].shape[0]
rows_kept_C = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_kept_clean_outside)].shape[0]
rows_dropped_A = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_contaminated)].shape[0]
rows_dropped_B = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_speed_limit_only)].shape[0]
rows_dropped_C = original_df_filtered[original_df_filtered['intersection_id'].isin(ids_dropped_never_treated)].shape[0]

print("\n--- Full Audit of All Rows (2013-2023) ---")
print(f"Total Rows in Original Data (2013-2023): {original_df_filtered.shape[0]:,}")
print("=" * 60)
print(f"  Rows KEPT (Clean History 2015-2021): {rows_kept_A:>20,}")
print(f"  Rows KEPT (Mixed History): {rows_kept_B:>29,}")
print(f"  Rows KEPT (Clean History outside): {rows_kept_C:>22,}")
print("-" * 60)
print(f"  Subtotal Kept Rows (Calculated): {rows_kept_A + rows_kept_B + rows_kept_C:>22,}")
print(f"  Actual Rows in Final File: {final_row_count:>28,}")
print("-" * 60)
print(f"  Rows DROPPED (Contaminated History): {rows_dropped_A:>21,}")
print(f"  Rows DROPPED (Speed Limit Only): {rows_dropped_B:>23,}")
print(f"  Rows DROPPED (Never Treated): {rows_dropped_C:>26,}")
print("-" * 60)
total_calculated_rows = rows_kept_A + rows_kept_B + rows_kept_C + rows_dropped_A + rows_dropped_B + rows_dropped_C
print(f"  GRAND TOTAL (All Categories): {total_calculated_rows:>27,}")

try:
    assert (rows_kept_A + rows_kept_B + rows_kept_C) == final_row_count
    assert total_calculated_rows == original_df_filtered.shape[0]
    print("\n✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
    print("CORRECTED AUDIT COMPLETE AND 100% SUCCESSFUL!")
    print("Every row has been perfectly accounted for using the R-aligned logic.")
    print("✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
except AssertionError:
    print("\n❌❌❌ VALIDATION FAILED! The row counts do not reconcile. ❌❌❌")

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

# In[4]:


# 2013-2016 minus intersections treated with anything but speed limit

# --- Setup: Load Data and Define Interventions ---

# Load the full intersection-year level dataset
try:
    intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')
    print(f"Successfully loaded data. Shape: {intersection_intervention_table.shape}")
except FileNotFoundError:
    print("Error: The file '../data/output/intersection_intervention_table_final.csv' was not found.")
    print("Please ensure the file path is correct and the original full dataset is available.")
    exit()

# Define the list of the 8 specific Vision Zero interventions you want to exclude
intersection_interventions = [
    'leading_pedestrian_interval_post', 
    'turn_traffic_calming_post', 
    'slow_zones_post', 
    'signal_retiming_post', 
    'speed_humps_post', 
    'street_improvement_project_post', 
    'street_improvement_corridors_post', 
    'enhanced_crossing_post'
]

# --- Step 1: Identify Intersections to Exclude ---

# Find all unique intersection_ids that EVER received one of the 8 specified interventions.
treated_intersection_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[intersection_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()

print(f"Found {len(treated_intersection_ids)} unique intersections that received at least one of the 8 VZ treatments.")

# --- Step 2: Create the 'Untreated' Dataset ---

# Filter the original dataframe to EXCLUDE the treated intersections identified above.
# This dataframe now contains only intersections that received 'speed_limit_only' or 'nothing'.
untreated_intersections_df = intersection_intervention_table[
    ~intersection_intervention_table['intersection_id'].isin(treated_intersection_ids)
].copy()

print(f"Filtered to 'untreated' intersections. Shape of this intermediate dataset: {untreated_intersections_df.shape}")


# --- Step 2.5: Create the 'source' Column (NEW SECTION) ---
# We add the indicator variable here, before the time cutoff, to ensure the classification
# is based on the entire history of each intersection.

# First, determine if an intersection EVER received the speed limit treatment.
untreated_intersections_df['ever_got_speed_limit'] = untreated_intersections_df.groupby('intersection_id')['speed_limit_post'].transform('max')

# Now, use np.where to create the 'source' column based on this check.
untreated_intersections_df['source'] = np.where(
    untreated_intersections_df['ever_got_speed_limit'] == 1, 
    'speed_limit_only', 
    'nothing'
)

# Drop the temporary helper column
untreated_intersections_df = untreated_intersections_df.drop(columns=['ever_got_speed_limit'])

print("Successfully created the 'source' column to identify intersection types.")


# --- Step 3: Apply the Time Cutoff (2013-2016) ---

# Now, limit the 'untreated' dataset to the years 2013 through 2016, inclusive.
untreated_robustness_df_2013_2016 = untreated_intersections_df[
    (untreated_intersections_df['year'] >= 2013) & (untreated_intersections_df['year'] <= 2016)
].copy()

print(f"Applied the 2013-2016 time cutoff.")
print(f"Final shape of the robustness check dataset: {untreated_robustness_df_2013_2016.shape}")

# --- Step 4: Save the New Dataset ---

# Save the resulting dataframe to a new CSV file for your robustness checks.
output_path = '../data/output/intersection_intervention_table_untreated_2013-2016.csv'
untreated_robustness_df_2013_2016.to_csv(output_path, index=False)

print(f"\nSuccessfully created and saved the robustness check dataset to:\n{output_path}")

# --- Step 5: Verification (EXPANDED SECTION) ---

print("\nVerification of the new dataset:")
# Check unique years to ensure the filter worked
years_in_df = sorted(untreated_robustness_df_2013_2016['year'].unique())
print(f"Unique years in the new dataset: {years_in_df}")

# Verify that none of the 8 intervention columns have a '1'
intervention_sums = untreated_robustness_df_2013_2016[intersection_interventions].sum().sum()
print(f"Sum of all 8 intervention columns in the new dataset: {intervention_sums} (should be 0)")


# --- NEW VERIFICATION STEPS for the 'source' column ---
print("\nVerifying the new 'source' column:")
# 1. Check the distribution of values in the 'source' column.
source_counts = untreated_robustness_df_2013_2016['source'].value_counts()
print("Value counts for the 'source' column:")
print(source_counts)

# 2. Perform a cross-tabulation to rigorously check the logic.
#    Since we created the 'source' column before filtering by year, this check confirms
#    that the labels are consistent within the final 2013-2016 dataframe.
crosstab_check = pd.crosstab(
    untreated_robustness_df_2013_2016['source'],
    untreated_robustness_df_2013_2016.groupby('intersection_id')['speed_limit_post'].transform('max'),
    rownames=['Source Label'],
    colnames=['Ever Received Speed Limit?']
)
print("\nCross-tabulation check (off-diagonals should be 0):")
print(crosstab_check)

if (crosstab_check.loc['nothing', 1] == 0) and (crosstab_check.loc['speed_limit_only', 0] == 0):
    print("\nVerification successful: 'source' column logic is correct.")
else:
    print("\nVerification FAILED: There is a mismatch in the 'source' column logic.")

# In[3]:


# 2013-2023 minus intersections treated with anything but speed limit

# --- Setup: Load Data and Define Interventions ---

# Load the full, original intersection-year level dataset
try:
    intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')
    print(f"Successfully loaded the full dataset. Shape: {intersection_intervention_table.shape}")
except FileNotFoundError:
    print("Error: The file '../data/output/intersection_intervention_table_final.csv' was not found.")
    print("Please ensure the file path is correct and the original full dataset is available.")
    exit()

# Define the list of the 8 specific Vision Zero interventions to use for exclusion
intersection_interventions = [
    'leading_pedestrian_interval_post', 
    'turn_traffic_calming_post', 
    'slow_zones_post', 
    'signal_retiming_post', 
    'speed_humps_post', 
    'street_improvement_project_post', 
    'street_improvement_corridors_post', 
    'enhanced_crossing_post'
]

# --- Step 1: Identify Intersections to Exclude ---

# Find all unique intersection_ids that EVER received one of the 8 specified interventions.
treated_intersection_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[intersection_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()

print(f"Found {len(treated_intersection_ids)} unique intersections that ever received one of the 8 VZ treatments.")

# --- Step 2: Create the 'Untreated' Dataset ---

# Filter the original dataframe to EXCLUDE the treated intersections identified above.
# This dataframe now contains only intersections that received 'speed_limit_only' or 'nothing'.
untreated_intersections_df = intersection_intervention_table[
    ~intersection_intervention_table['intersection_id'].isin(treated_intersection_ids)
].copy()

print(f"Filtered to 'untreated' intersections. Shape of this intermediate dataset: {untreated_intersections_df.shape}")


# --- Step 2.5: Create the 'source' Column (NEW SECTION) ---
# Here we add the indicator variable to distinguish between the two types of intersections remaining.

# To do this efficiently, we first determine if an intersection EVER received the speed limit.
# We use groupby() and transform('max') to check the entire history of each intersection.
# This creates a temporary series where each row's value is the max 'speed_limit_post' for its intersection_id.
untreated_intersections_df['ever_got_speed_limit'] = untreated_intersections_df.groupby('intersection_id')['speed_limit_post'].transform('max')

# Now, use np.where to create the 'source' column based on this check.
# If 'ever_got_speed_limit' is 1, the source is 'speed_limit_only'.
# If it's 0, the source is 'nothing'.
untreated_intersections_df['source'] = np.where(
    untreated_intersections_df['ever_got_speed_limit'] == 1, 
    'speed_limit_only', 
    'nothing'
)

# We can now drop the temporary helper column
untreated_intersections_df = untreated_intersections_df.drop(columns=['ever_got_speed_limit'])

print("Successfully created the 'source' column to identify intersection types.")


# --- Step 3: Apply the NEW, EXTENDED Time Cutoff (2013-2023) ---

# Limit the 'untreated' dataset to the years 2013 through 2023, inclusive.
untreated_robustness_df_2013_2023 = untreated_intersections_df[
    (untreated_intersections_df['year'] >= 2013) & (untreated_intersections_df['year'] <= 2023)
].copy()

print(f"Applied the 2013-2023 time cutoff.")
print(f"Final shape of the new extended dataset: {untreated_robustness_df_2013_2023.shape}")

# --- Step 4: Save the New Extended Dataset ---

# Save the resulting dataframe to a new CSV file with a descriptive name.
output_path = '../data/output/intersection_intervention_table_untreated_2013-2023.csv'
untreated_robustness_df_2013_2023.to_csv(output_path, index=False)

print(f"\nSuccessfully created and saved the extended robustness check dataset to:\n{output_path}")

# --- Step 5: Verification (EXPANDED SECTION) ---

print("\nVerification of the new dataset:")
# Check unique years to ensure the filter worked
years_in_df = sorted(untreated_robustness_df_2013_2023['year'].unique())
print(f"Years included in the new dataset: {years_in_df[0]} through {years_in_df[-1]}")

# Verify that none of the 8 intervention columns have a '1'
intervention_sums = untreated_robustness_df_2013_2023[intersection_interventions].sum().sum()
print(f"Sum of all 8 intervention columns in the new dataset: {intervention_sums} (should be 0)")

# --- NEW VERIFICATION STEPS for the 'source' column ---
print("\nVerifying the new 'source' column:")
# 1. Check the distribution of values in the 'source' column.
#    This confirms that only our two expected values exist.
source_counts = untreated_robustness_df_2013_2023['source'].value_counts()
print("Value counts for the 'source' column:")
print(source_counts)

# 2. Perform a cross-tabulation to rigorously check the logic.
#    We check if intersections labeled 'nothing' truly never have 'speed_limit_post' = 1.
#    And if intersections labeled 'speed_limit_only' do have 'speed_limit_post' = 1 at some point.
crosstab_check = pd.crosstab(
    untreated_robustness_df_2013_2023['source'],
    untreated_robustness_df_2013_2023.groupby('intersection_id')['speed_limit_post'].transform('max'),
    rownames=['Source Label'],
    colnames=['Ever Received Speed Limit?']
)
print("\nCross-tabulation check (off-diagonals should be 0):")
print(crosstab_check)

if (crosstab_check.loc['nothing', 1] == 0) and (crosstab_check.loc['speed_limit_only', 0] == 0):
    print("\nVerification successful: 'source' column logic is correct.")
else:
    print("\nVerification FAILED: There is a mismatch in the 'source' column logic.")

# In[16]:


# 2013-2023 with ONLY solely speed limit 

# --- Setup: Load Data and Define Interventions ---

# Load the full, original intersection-year level dataset
try:
    intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')
    print(f"Successfully loaded the full dataset. Shape: {intersection_intervention_table.shape}")
except FileNotFoundError:
    print("Error: The file '../data/output/intersection_intervention_table_final.csv' was not found.")
    print("Please ensure the file path is correct and the original full dataset is available.")
    exit()

# Define the list of the 8 "complex" VZ interventions
main_interventions = [
    'leading_pedestrian_interval_post', 
    'turn_traffic_calming_post', 
    'slow_zones_post', 
    'signal_retiming_post', 
    'speed_humps_post', 
    'street_improvement_project_post', 
    'street_improvement_corridors_post', 
    'enhanced_crossing_post'
]

# Define the list of ALL 9 interventions
all_interventions = main_interventions + ['speed_limit_post']

# --- Step 1: Identify Intersection Groups to Exclude ---

# Group 1: Find all IDs that EVER received one of the 8 main interventions. These will be excluded.
complex_treated_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[main_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()
print(f"Found {len(complex_treated_ids)} unique intersections that received at least one of the 8 main VZ treatments.")

# Group 2: Find all IDs that were NEVER treated with ANYTHING. These will also be excluded.
# First, find all IDs that received at least one of the 9 total interventions.
any_treated_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[all_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()

# Now, find the purely untreated IDs by taking the set difference
all_intersection_ids = set(intersection_intervention_table['intersection_id'].unique())
purely_untreated_ids = all_intersection_ids - set(any_treated_ids)
print(f"Found {len(purely_untreated_ids)} unique intersections that received no interventions at all.")

# Combine the two groups of IDs to exclude
ids_to_exclude = set(complex_treated_ids).union(purely_untreated_ids)
print(f"Total unique intersections to exclude: {len(ids_to_exclude)}")


# --- Step 2: Create the "Speed Limit Only" Dataset ---

# Filter the original dataframe to keep only the intersections NOT in the exclusion list.
# The remaining intersections are the ones treated with speed limit ONLY.
speed_limit_only_df = intersection_intervention_table[
    ~intersection_intervention_table['intersection_id'].isin(ids_to_exclude)
].copy()

print(f"Filtered to 'speed limit only' intersections. Shape of this intermediate dataset: {speed_limit_only_df.shape}")

# --- Step 3: Apply the Time Cutoff (2013-2023) ---

# Limit the 'speed limit only' dataset to the years 2013 through 2023, inclusive.
speed_limit_only_df_2013_2023 = speed_limit_only_df[
    (speed_limit_only_df['year'] >= 2013) & (speed_limit_only_df['year'] <= 2023)
].copy()

print(f"Applied the 2013-2023 time cutoff.")
print(f"Final shape of the 'speed limit only' dataset: {speed_limit_only_df_2013_2023.shape}")

# --- Step 4: Save the New Dataset ---

# Save the resulting dataframe to a new CSV file with a clear, descriptive name.
output_path = '../data/output/intersection_table_speed_limit_only_2013-2023.csv'
speed_limit_only_df_2013_2023.to_csv(output_path, index=False)

print(f"\nSuccessfully created and saved the 'speed limit only' dataset to:\n{output_path}")

# --- Verification ---
print("\nVerifying the contents of the new dataset:")
# Check that none of the 8 main intervention columns have a '1'
main_intervention_sum = speed_limit_only_df_2013_2023[main_interventions].sum().sum()
print(f"Sum of all 8 main intervention columns: {main_intervention_sum} (should be 0)")

# Check that the 'speed_limit_post' column has some '1's, confirming these intersections were treated.
speed_limit_sum = speed_limit_only_df_2013_2023['speed_limit_post'].sum()
print(f"Sum of the 'speed_limit_post' column: {speed_limit_sum} (should be > 0)")


# In[17]:


# 2013-2016 with ONLY solely speed limit 

# --- Setup: Load Data and Define Interventions ---

# Load the full, original intersection-year level dataset
try:
    intersection_intervention_table = pd.read_csv('../data/output/intersection_intervention_table_final.csv')
    print(f"Successfully loaded the full dataset. Shape: {intersection_intervention_table.shape}")
except FileNotFoundError:
    print("Error: The file '../data/output/intersection_intervention_table_final.csv' was not found.")
    print("Please ensure the file path is correct and the original full dataset is available.")
    exit()

# Define the list of the 8 "complex" VZ interventions
main_interventions = [
    'leading_pedestrian_interval_post', 
    'turn_traffic_calming_post', 
    'slow_zones_post', 
    'signal_retiming_post', 
    'speed_humps_post', 
    'street_improvement_project_post', 
    'street_improvement_corridors_post', 
    'enhanced_crossing_post'
]

# Define the list of ALL 9 interventions
all_interventions = main_interventions + ['speed_limit_post']

# --- Step 1: Identify Intersection Groups to Exclude ---

# This logic is identical to the previous script. We identify intersections based on their entire history.

# Group 1: Find all IDs that EVER received one of the 8 main interventions.
complex_treated_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[main_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()
print(f"Found {len(complex_treated_ids)} unique intersections that received at least one of the 8 main VZ treatments.")

# Group 2: Find all IDs that were NEVER treated with ANYTHING.
any_treated_ids = intersection_intervention_table.loc[
    (intersection_intervention_table[all_interventions] == 1).any(axis=1), 
    'intersection_id'
].unique()
all_intersection_ids = set(intersection_intervention_table['intersection_id'].unique())
purely_untreated_ids = all_intersection_ids - set(any_treated_ids)
print(f"Found {len(purely_untreated_ids)} unique intersections that received no interventions at all.")

# Combine the two groups of IDs to exclude
ids_to_exclude = set(complex_treated_ids).union(purely_untreated_ids)
print(f"Total unique intersections to exclude: {len(ids_to_exclude)}")


# --- Step 2: Create the "Speed Limit Only" Dataset ---

# Filter the original dataframe to keep only the intersections NOT in the exclusion list.
speed_limit_only_df = intersection_intervention_table[
    ~intersection_intervention_table['intersection_id'].isin(ids_to_exclude)
].copy()

print(f"Filtered to 'speed limit only' intersections. Shape of this intermediate dataset: {speed_limit_only_df.shape}")

# --- Step 3: Apply the SHORTER Time Cutoff (2013-2016) ---

# Limit the 'speed limit only' dataset to the years 2013 through 2016, inclusive.
# This is the key change from the last script.
speed_limit_only_df_2013_2016 = speed_limit_only_df[
    (speed_limit_only_df['year'] >= 2013) & (speed_limit_only_df['year'] <= 2016)
].copy()

print(f"Applied the 2013-2016 time cutoff.")
print(f"Final shape of the 'speed limit only' 2013-2016 dataset: {speed_limit_only_df_2013_2016.shape}")

# --- Step 4: Save the New Dataset ---

# Save the resulting dataframe to a new CSV file with a clear, descriptive name.
output_path = '../data/output/intersection_table_speed_limit_only_2013-2016.csv'
speed_limit_only_df_2013_2016.to_csv(output_path, index=False)

print(f"\nSuccessfully created and saved the 'speed limit only' (2013-2016) dataset to:\n{output_path}")

# --- Verification ---
print("\nVerifying the contents of the new dataset:")
# Check unique years
print(f"Unique years in final dataset: {sorted(speed_limit_only_df_2013_2016['year'].unique())}")
# Check that none of the 8 main intervention columns have a '1'
main_intervention_sum = speed_limit_only_df_2013_2016[main_interventions].sum().sum()
print(f"Sum of all 8 main intervention columns: {main_intervention_sum} (should be 0)")
# Check that the 'speed_limit_post' column has some '1's
speed_limit_sum = speed_limit_only_df_2013_2016['speed_limit_post'].sum()
print(f"Sum of the 'speed_limit_post' column: {speed_limit_sum} (should be > 0)")
