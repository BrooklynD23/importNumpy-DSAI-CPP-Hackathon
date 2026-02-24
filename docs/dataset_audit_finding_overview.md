# Dataset Audit Finding Overview

Generated: 2026-02-24
Dataset: `Raw Dataset/Global Health Statistics.csv`
Working table audited: `raw_health` in `data/health.duckdb`

## 1) Scope and Question

This audit addresses:
1. Whether the dataset is synthetic.
2. What evidence supports that conclusion.
3. Why this matters for analysis, conclusions, and recommendations.

## 2) Executive Conclusion

The dataset is synthetic with very high confidence.

Reason: multiple independent signatures are consistent with synthetic generation (or heavy synthetic balancing): near-complete Cartesian coverage of category combinations, near-zero dependence structure across all major numeric variables, bounded-variable distributions that closely match uniform-range draws, implausibly homogeneous country/year aggregates, and randomized disease-category labeling behavior.

Important caveat: this is a statistical/structural verification, not provenance proof. Absolute proof of origin requires metadata from the data provider.

## 3) Evidence Summary (Measured)

### A. Structural coverage and repeated-combination behavior

- Total rows: `1,000,000`
- Distinct dimensions: `20 countries`, `25 years (2000-2024)`, `20 diseases`, `4 age groups`, `3 genders`
- Maximum possible `(country, year, disease, age_group, gender)` combinations:
  `20 * 25 * 20 * 4 * 3 = 120,000`
- Observed combinations: `119,978` (`99.9817%` coverage)
- Mean rows per observed combination: `8.3349`
- Combinations with duplicates (`count > 1`): `119,731`

Interpretation: this is near-Cartesian design coverage plus repeated sampling per cell, a strong synthetic-data signature.

### B. Dependence structure is effectively absent

- Maximum absolute Pearson correlation among 14 numeric columns:
  `|r|max = 0.0023368` (`incidence_rate` vs `population_affected`)
- Domain-critical correlations:
  - `corr(healthcare_access, mortality_rate) = 0.0000772`
  - `corr(healthcare_access, recovery_rate) = 0.0015980`
  - `corr(per_capita_income, healthcare_access) = -0.0013083`
  - `corr(per_capita_income, mortality_rate) = -0.0015034`
  - `corr(education_index, healthcare_access) = 0.0010848`
  - `corr(education_index, mortality_rate) = -0.0001103`
  - `corr(urbanization_rate, healthcare_access) = 0.0003628`

Interpretation: real population health data usually exhibits some non-trivial structure in at least a subset of these relationships; here the entire system is almost independent.

### C. Bounded-rate variables match uniform-range behavior

For bounded columns, observed means and standard deviations nearly match Uniform(a,b) expectations:

- `mortality_rate`: mean `5.0499` vs expected midpoint `5.05`; sd `2.8594` vs uniform sd `2.8579`
- `healthcare_access`: mean `74.9878` vs midpoint `75.0`; sd `14.4363` vs uniform sd `14.4338`
- `recovery_rate`: mean `74.4969` vs midpoint `74.5`; sd `14.1552` vs uniform sd `14.1451`
- Similar midpoint/sd closeness observed for `prevalence_rate`, `incidence_rate`, `improvement_in_5_years`, `urbanization_rate`

Interpretation: this is consistent with generated values from fixed bounded ranges.

### D. Country/year aggregates are implausibly homogeneous

Country-level mean spread:
- Mortality mean by country: min `5.0309`, max `5.0749`, sd `0.0134`
- Recovery mean by country: min `74.4009`, max `74.6045`, sd `0.0556`
- Access mean by country: min `74.8807`, max `75.1732`, sd `0.0735`

Year-level mean spread:
- Mortality mean by year: min `5.0259`, max `5.0710`, sd `0.0103`
- Access mean by year: min `74.8224`, max `75.1427`, sd `0.0786`

ANOVA effect size:
- Eta-squared for `mortality_rate ~ country`: `2.0773e-05`

Interpretation: geographic and temporal effects are effectively negligible at a scale where real systems normally show stronger heterogeneity.

### E. Disease-category label behavior is random-like

- Every disease has `11/11` distinct values in `disease_category_original`.
- Mean entropy of category distribution within each disease: `3.45929`
- Maximum possible entropy for 11 categories: `log2(11) = 3.45943`
- Gap to maximum entropy: `0.00014` (near maximal uniformity)
- Cramer's V for `(disease_name, disease_category_original)`: `0.0` (chi-square p-value `0.5428`)

Interpretation: disease labels and original categories are nearly independent and near-uniformly mixed, which is inconsistent with real disease taxonomy.

### F. Numeric precision pattern

- Across audited numeric columns, rows with non-2-decimal values: `0`

Interpretation: strict global 2-decimal quantization is another generated-data trait (not impossible in real data, but uncommon when all measures share it).

## 4) Why This Matters

### A. Causal and policy interpretation risk

If data is synthetic/randomly generated, then:
- "No relationship" findings can be generator artifacts, not real-world evidence.
- Any policy recommendation tied to inferred drivers (access, income, education, urbanization) is weakly justified.
- Effect estimates and confidence intervals quantify synthetic variance, not operational uncertainty from real systems.

### B. External validity and model transfer risk

- Models trained here will likely learn generator structure, not healthcare mechanisms.
- Feature importance, thresholds, and interventions are unlikely to generalize to real populations.

### C. Competition communication strategy

For this datathon prompt, the strongest analytical posture is:
- Explicitly separate what the dataset can support vs cannot support.
- Avoid overclaiming causality.
- Treat synthetic detection itself as a meta-finding tied to Question 6 ("premature conclusions").

## 5) Source Citations (Repo Files)

### Primary audit/report artifacts

- `reports/data_quality_report.md:1-94`
- `reports/data_quality_report.md:34-49` (hard bounds/ranges)
- `reports/data_quality_report.md:53` (duplicate-group volume)
- `reports/data_quality_report.md:55-78` (every disease mapped across all 11 categories)

### Pipeline logic that defines what Phase 2 verifies

- `pipeline/phase2_profile.py:33-51` (missingness profiling)
- `pipeline/phase2_profile.py:60-79` (range checks)
- `pipeline/phase2_profile.py:90-100` (duplicate-group audit)
- `pipeline/phase2_profile.py:110-121` (disease-category reliability audit)

### Internal project docs/analysis that already flag synthetic behavior

- `docs/plan-2-13.md:5` (explicit synthetic-data claim)
- `docs/plan-2-13.md:11-16` (near-zero relationship and homogeneity summary)
- `notebooks/q2_access_vs_outcomes.ipynb:254`
- `notebooks/q3_outlier_communities.ipynb:286`
- `notebooks/q6_premature_conclusions.ipynb:348`
- `notebooks/summary_executive.ipynb:296`

## 6) Reproducibility Notes

The measured values in this overview were recomputed directly against `data/health.duckdb` (`raw_health`) using DuckDB SQL and Python (`.venv/bin/python`, `duckdb`, `numpy`, `scipy`). They can be re-run deterministically from the current repository state.

## 7) Confidence Statement

Confidence in "synthetic or heavily synthetic-balanced data": very high.

Confidence in strict provenance claim ("generated by specific tool/process"): low without external metadata from the data source owner.
