# One‑Pager — Team importNumpy (DND Spring 2026 Datathon)

## Problem
The prompt asks what drives geographic disparities in health outcomes (and warns about uncertainty and premature conclusions). We were given a 1M-row “global health” dataset across countries, years, diseases, demographics, and access proxies.

## What we found (headline)
**This dataset behaves like synthetic or heavily synthetic-balanced data.**  
It is clean and plausible-looking, but lacks the dependence structure and heterogeneity that real-world health systems exhibit.

## What we measured vs what’s missing
- **Measured:** outcomes (mortality/recovery/DALYs), access proxies (healthcare_access, doctors, beds), socioeconomic proxies (income/education), geography proxy (urbanization tiers).
- **Missing:** distance-to-care and utilization (no travel time, proximity, facility locations, visits/admissions).

## Top findings (Evidence Ladder labeled)
1) **Geographic disparities are absent** (**Descriptive**)  
Urban/rural tiers show near-zero effect sizes; country profiles are nearly identical.

2) **Access proxies do not predict outcomes** (**Descriptive**)  
Access↔mortality/recovery relationships are ~0 across groups.

3) **“Outliers” are statistical artifacts** (**Descriptive**)  
Some z-scores appear large due to tiny variance, but absolute differences are noise-level.

4) **Tier definitions don’t change conclusions** (**Robustness**)  
3-tier vs binary vs 4-tier schemes yield the same flat results.

5) **Results are stable under dedup-at-cell-grain robustness** (**Robustness**)  
Aggregating repeated (country, year, disease, age, gender) cells does not change conclusions.

## What would be premature to conclude (Q6)
- Any causal/policy statement like “improve access to reduce mortality” is not supported by this dataset’s structure.
- Resource reallocation decisions based on these null patterns would be unjustified.

## What we recommend (safe next steps)
1) Validate provenance + generation process of the dataset (metadata audit).  
2) Collect/merge **distance-to-care** and **utilization** measures (travel time, facility density, admissions/visits).  
3) Re-run the same pipeline + robustness checks; only then move toward intervention design.

## Reproducibility
One command regenerates everything: `bash run.sh`  
Key outputs: `reports/summary_executive.html`, `reports/q*.html`, `reports/figures/*.png`.

