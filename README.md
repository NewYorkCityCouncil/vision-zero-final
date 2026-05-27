# Vision Zero Analysis
This repository holds the code for the Data Team's analysis of Vision Zero, an NYC initiative launched in 2014 that aims to reduce traffic fatalities in the City to zero. An associated pre-print for this analysis may be accessed through [this link](https://zenodo.org/records/18774081). The study has also been conditionally approved for publication in the Journal of Safety Research, pending final revisions.

***

## Summary and Intention

### Motivation
Despite advancements in vehicle safety, motor vehicle crashes remain a leading cause of mortality globally and in the United States. In 2014, NYC adopted the Vision Zero framework, shifting the perspective of traffic collisions from isolated human errors to a systemic public health issue. Till now, few studies have assessed the NYC VZ program, and ones that have were limited in scope and/or methodology. Our analysis aims to fill this gap by disaggregatig the impacts of nine different NYC VZ interventions.

### Research Questions
* Have NYC VZ on-street interventions successfully reduced the number of pedestrian casualties (deaths and injuries) resulting from motor vehicle collisions?
* Controlling for the overlapping rollout of multiple safety treatments, which specific physical and regulatory interventions provide the greatest protective benefits for pedestrians?

## Methodology 

### Datasets (data/input/ directory):

- [Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)
- [LION Dataset](https://www.nyc.gov/content/planning/pages/resources/datasets/lion)
- DOT Internal Data: Crashes with intersection IDs (available in data/input/dot_data)
- [NYC Planimetrics Database: Roadbed](https://data.cityofnewyork.us/Transportation/NYC-Planimetric-Database-Roadbed/i36f-5ih7/about_data)
- [NYPD Criminal Court Summonses](https://data.cityofnewyork.us/Public-Safety/NYPD-Criminal-Court-Summons-Incident-Level-Data-Ye/mv4k-y93f/about_data)
- [US Federal Highway Administration: Miles and Daily Vehicle - Miles Traveled](https://www.fhwa.dot.gov/policyinformation/travel_monitoring/tvt.cfm)
- [VZV Speed Limits](https://data.cityofnewyork.us/Transportation/VZV-Speed-Limits/5mad-ntua/about_data)
- [VZV Speed Humps](https://data.cityofnewyork.us/Transportation/VZV-Speed-Humps/jknp-skuy/about_data)
- [VZV Leading Pedestrian Interval Signals](https://data.cityofnewyork.us/Transportation/VZV-Leading-Pedestrian-Interval-Signals/xc4v-ntf4/about_data)
- [VZV Enhanced Crossings](https://data.cityofnewyork.us/Transportation/VZV-Enhanced-Crossings/6ax4-q5k4/about_data)
- [VZV Turn Traffic Calming](https://data.cityofnewyork.us/Transportation/VZV-Turn-Traffic-Calming/sm2x-35i7/about_data)
- [VZV Neighborhood Slow Zones](https://data.cityofnewyork.us/Transportation/VZV-Neighborhood-Slow-Zones/bqye-aqft/about_data)
- [VZV Signal Retiming](https://data.cityofnewyork.us/Transportation/VZV-Signal-Timing-25MPH-Signal-Retiming/d8dp-wfee/about_data)
- [VZV Street Improvement Projects Intersections](https://data.cityofnewyork.us/Transportation/VZV-Street-Improvement-Projects-SIP-Intersections/shr7-eqdc/about_data)
- [VZV Street Improvement Projects Corridor](https://data.cityofnewyork.us/Transportation/VZV-Street-Improvement-Projects-SIP-Corridor/if4c-w48d/about_data)

### Statistical Analysis 
* **Study Design:** Staggered difference-in-difference (DiD) analysis evaluating nine distinct VZ interventions over an 11-year period (2013–2023). 
* **Sample:** 9,562 treated intersections, 105,182 intersection-year observations. 
* **Modeling:** Fixed-effects negative binomial regression model with annual pedestrian deaths and injuries at the intersection level as the outcome.
* **Controls:** Intersection-level fixed effects (accounting for time-invariant traits like geometry), annual traffic volume, traffic enforcement intensity (criminal summonses), population density, a COVID-19 pandemic indicator, and a linear time trend.
* **Parallel Trends Assumption:** Validated using descriptive cohort plots, a global event study, and nine intervention-specific event studies.

### Scripts (code/ directory)

#### 00_upload_lion.Rmd
Saves usable LION dataset.

#### 01_clean_lion_dataset.ipynb
Cleaning LION data to obtain street geometries.

#### 02_clean_node_dataset.ipynb
Obtaining intersection geometries using LION node data.

#### 03_add_collisions.ipynb
Adding information about collisions in NYC.

#### 04_build_vz_table.ipynb
Building final table shell.

#### 05_add_interventions.ipynb
Adding intervention-years into the table.

#### 06_add_controls.ipynb
Adding controls columns and rows into the table.

#### 07_prep_dataset_for_analysis.ipynb
Prepping various datasets (including final analytic dataset and sensitivity analysis data) for analysis, using different inclusion/exclusion criteria. 

#### 08_eda.ipynb
Visualization and EDA.

#### 09_model_fixed_effects.Rmd
Final fixed effects NB model with diagnostics. 

#### 10_speed_limit_fixed_effects.Rmd
Final sensitivity analysis models for speed limit change. 

#### 11_event_study_fixed_effects.Rmd
Event study to check parallel trends assumption. 

## Results
We identified four interventions that were associated with statistically significant reductions in annual pedestrian casualties:
* **Turn Traffic Calming:** 27% reduction (Incidence Rate Ratio [IRR] 0.73, 95% CI: 0.64, 0.85).
* **Neighborhood Slow Zones:** 21% reduction (IRR 0.79, 95% CI: 0.66, 0.94).
* **Leading Pedestrian Interval (LPI) Signals:** IRR 0.87 (95% CI: 0.82, 0.93).
* **Citywide Speed Limit Reduction (30 to 25 MPH):** IRR 0.90 (95% CI: 0.85, 0.95).

## Conclusions
* **Scale up proven interventions:** Policymakers and transportation planners should concentrate funding and resources on interventions that physically or regulatorily compel slower vehicle speeds (e.g., Turn Traffic Calming, Neighborhood Slow Zones) and interventions that increase pedestrian visibility by separating signal phasing (e.g., LPIs). 
* **Investigate null findings contextually:** The lack of significant benefit for interventions like enhanced crossings or SIPs does not mean they should be universally abandoned. Agencies should conduct targeted, site-specific evaluations to learn how these tools can be deployed more effectively.

