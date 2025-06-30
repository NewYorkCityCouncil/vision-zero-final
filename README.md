## Vision Zero Analysis

This repo holds the code for the Data Team's analysis of Vision Zero, an NYC initiative launched in 2014 that aims to reduce traffic fatalities in the city to zero. 

#### Datasets Used:

Datasets:
- Motor Vehicle Collisions - Crashes
- LION Dataset
- DOT-provided: Crashes with intersection IDs (connects collision dataset to LION)
- NYC Planimetrics Database: Roadbed
- NYPD Criminal Court Summonses
- US Federal Highway Administration: Miles and Daily Vehicle - Miles Traveled
- VZV Speed Limits
- VZV Speed Humps
- VZV Leading Pedestrian Interval Signals
- VZV Enhanced Crossings
- VZV Left Turn Traffic Calming
- VZV Neighborhood Slow Zones
- VZV Signal Timing
- VZV Street Improvement Projects Intersections
- VZV Street Improvement Projects Corridor

#### Model

For this analysis, we employed a negative binomial regression model to account for overdispersion in the outcome data (dispersion statistic: 1.62). The model was deployed using the glmmTMB package in R, incorporating fixed effects for the interventions and control variables, along with nested random intercepts for boroughs, NTAs, and intersections to account for baseline heterogeneity across multiple spatial scales. The relationship between population density and the number of pedestrian casualties was modeled using a natural spline with 2 degrees of freedom to capture evident nonlinearity. To account for heteroskedasticity, we calculated cluster-bootstrap robust standard errors. 

#### Results

Overall, pedestrian casualties in the city decreased during the observation period. After controlling for this downward trend, significant, negative associations with pedestrian casualties were still found for the citywide speed limit reduction (IRR 0.95, 95% CI 0.90 to 0.99), neighborhood slow zones (IRR 0.82, 95% CI 0.65 to 0.96), speed humps (IRR 0.87, 95% CI 0.78 to 0.95), SIP corridors (IRR 0.95, 95% CI 0.90 to 0.99), and turn traffic calming (IRR 0.83, 95% CI 0.72 to 0.91). A small, but significant positive association was found for 25 MPH signal retiming (IRR 1.07, 95% CI 1.02 to 1.11), representing a 6.8% increase. Enhanced crossings, leading pedestrian interval signals, and SIP intersections did not demonstrate any significant impact on pedestrian casualties. Neighborhood slow zones and turn traffic calming stand out as having the largest effects, at -17.6% and -17.2%, respectively. The majority of residual variance was at the intersection level (SD = 1.14), followed by NTA (SD = 0.51) and borough (SD = 0.27), indicating substantial variation in pedestrian injury rates across these spatial units. 

