# Prompt → Data Contract (Team importNumpy)

This document is our “rules of engagement” for analysis. It makes explicit:
1) what the datathon prompt asks,  
2) what this dataset *actually* measures, and  
3) what kinds of conclusions we will (and will not) claim.

If a judge challenges an inference (“Where is distance-to-care measured?” / “Is this causal?”), this is the reference.

---

## 1) Evidence Ladder (how strong is a claim?)

All major claims must be labeled as one of:

### A) Descriptive (Observed)
**Meaning:** “This is what the provided dataset contains.”  
**Allowed:** distributions, group averages, effect sizes, uncertainty summaries, correlation estimates.  
**Not allowed:** causal language (“causes”, “leads to”) or policy prescriptions that assume real-world validity.

### B) Robustness (Sensitivity / Stability)
**Meaning:** “The descriptive result is stable under reasonable re-aggregation or definitions.”  
**Allowed:** dedup-at-cell-grain checks, alternative tier schemes, resampling/subsampling, key-join integrity checks.

### C) Illustrative (Benchmark / Simulation)
**Meaning:** “This is what *realistic* data patterns often look like; used to explain expected signal, not to assert truth about this dataset.”  
**Allowed:** clearly labeled benchmark comparisons, “expected vs observed” panels, hypothetical action plans.  
**Not allowed:** mixing benchmark outputs into the core dataset or presenting benchmarks as measured.

**Default policy:** If a claim is not explicitly labeled, treat it as **not approved**.

---

## 2) What the Dataset Measures (and what it does not)

### Measured (available columns / derived fields)
- **Outcomes:** `mortality_rate`, `recovery_rate`, `dalys`
- **Access / supply proxies:** `healthcare_access`, `doctors_per_1000`, `hospital_beds_per_1000`, derived `resource_index`, derived `access_composite`
- **Socioeconomic proxies:** `per_capita_income`, `education_index`
- **Geography proxy:** `urbanization_rate` and derived tier schemes (3-tier + sensitivity schemes)
- **Population / burden:** `population_affected`
- **Structure:** `country`, `year`, `disease_name`, `age_group`, `gender`

### Not measured (hard limitations)
- **Distance-to-care / proximity:** no distance, travel time, facility density, or geodesic variables.
- **Utilization:** no visits, admissions, claims, continuity-of-care, etc.
- **Real-world heterogeneity signals:** the dataset exhibits strong synthetic signatures (see synthetic diagnostics artifacts).

---

## 3) Prompt Fit: Q1–Q6 mapping (SMART + defensible)

| Prompt question | Required concept | What we can measure here | Proxy used | What we *cannot* claim | Evidence ladder focus |
|---|---|---|---|---|---|
| Q1: Geographic outcome disparities | Geography differences | outcomes by `urbanization_tier` and `country` | urbanization tiers | “Rural causes worse outcomes” | Descriptive + Robustness (effect sizes, tier sensitivity) |
| Q2: Distance → utilization/outcomes | Distance, utilization | access/outcome association | `healthcare_access`, `resource_index` | any statement about *distance* specifically | Descriptive + Illustrative (“distance not measured”) |
| Q3: Communities defying access assumptions | Outliers vs expectations | country-level z-scores on access vs outcomes | z-scores from aggregates | “This country is truly exceptional” without practical effect | Descriptive + Robustness (scale vs significance) |
| Q4: Sensitivity to category definitions | Definition dependence | multiple tier schemes | default + alt tiers | “Tier choice changes conclusions” unless effect sizes shift | Robustness (compare schemes) |
| Q5: Uncertainty from sparse reporting | Missingness/small-N | CI widths by group | subsampling demonstration | “Low-income regions under-report” (not observed here) | Descriptive + Illustrative (simulate sparsity) |
| Q6: Premature conclusions | Inference limits | correlation structure, confounding proxies | correlation/entropy checks | policy recommendations from null/flat structure | Descriptive + Illustrative (expected-vs-observed) |

---

## 4) Standard language (copy/paste)

### Measurement gap (distance/utilization)
> The prompt asks about distance-to-care and utilization, but those variables are not present in this dataset. We therefore analyze *access proxies* (healthcare_access, doctors, beds) and explicitly treat any “distance” narrative as **unmeasured**.

### Synthetic signature / external validity
> Multiple independent diagnostics indicate the dataset behaves like synthetic or heavily synthetic-balanced data (near-Cartesian coverage, near-zero dependence, uniform-like bounded distributions). As a result, our results are **descriptive of this dataset** and should not be interpreted as causal evidence for real-world policy.

### Safe recommendation boundary
> Given the lack of real-world structure, our recommendations focus on **data validation and data collection requirements** needed before any resource reallocation decision, rather than prescribing interventions from this dataset alone.

