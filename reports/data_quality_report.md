# Data Quality Report
Generated: (see reports/_run_metadata.json)

## Missingness by Column

| Column | NULLs | % | Flagged |
|--------|-------|---|---------|
| row_id | 0 | 0.0000% |  |
| country | 0 | 0.0000% |  |
| year | 0 | 0.0000% |  |
| disease_name | 0 | 0.0000% |  |
| disease_category_original | 0 | 0.0000% |  |
| prevalence_rate | 0 | 0.0000% |  |
| incidence_rate | 0 | 0.0000% |  |
| mortality_rate | 0 | 0.0000% |  |
| age_group | 0 | 0.0000% |  |
| gender | 0 | 0.0000% |  |
| population_affected | 0 | 0.0000% |  |
| healthcare_access | 0 | 0.0000% |  |
| doctors_per_1000 | 0 | 0.0000% |  |
| hospital_beds_per_1000 | 0 | 0.0000% |  |
| treatment_type | 0 | 0.0000% |  |
| avg_treatment_cost_usd | 0 | 0.0000% |  |
| vaccine_treatment_available | 0 | 0.0000% |  |
| recovery_rate | 0 | 0.0000% |  |
| dalys | 0 | 0.0000% |  |
| improvement_in_5_years | 0 | 0.0000% |  |
| per_capita_income | 0 | 0.0000% |  |
| education_index | 0 | 0.0000% |  |
| urbanization_rate | 0 | 0.0000% |  |
| urbanization_tier | 0 | 0.0000% |  |
| resource_index | 0 | 0.0000% |  |

## Rate Column Ranges (expected 0–100)

| Column | Min | Max | Out-of-range Count |
|--------|-----|-----|--------------------|
| prevalence_rate | 0.10 | 20.00 | 0 |
| incidence_rate | 0.10 | 15.00 | 0 |
| mortality_rate | 0.10 | 10.00 | 0 |
| recovery_rate | 50.00 | 99.00 | 0 |
| improvement_in_5_years | 0.00 | 10.00 | 0 |
| healthcare_access | 50.00 | 100.00 | 0 |
| urbanization_rate | 20.00 | 90.00 | 0 |

## Cost and Income Ranges

- **avg_treatment_cost_usd**: min=100.00, max=50000.00, negative=0
- **per_capita_income**: min=500.00, max=100000.00, negative=0

## Duplicate Check

Duplicate groups (country × year × disease × age × gender): **119,731**

## Disease Category Reliability Audit

| Disease | # Original Categories | Categories |
|---------|----------------------|------------|
| Alzheimer's Disease | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Asthma | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| COVID-19 | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Cancer | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Cholera | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Dengue | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Diabetes | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Ebola | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| HIV/AIDS | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Hepatitis | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Hypertension | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Influenza | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Leprosy | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Malaria | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Measles | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Parkinson's Disease | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Polio | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Rabies | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Tuberculosis | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |
| Zika | 11 | ['Autoimmune', 'Bacterial', 'Cardiovascular', 'Chronic', 'Genetic', 'Infectious', 'Metabolic', 'Neurological', 'Parasitic', 'Respiratory', 'Viral'] |

## Small-N Countries (< 30 observations)

No countries with fewer than 30 observations.

## Distinct Value Inventory

- **disease_name** (20): Alzheimer's Disease, Asthma, COVID-19, Cancer, Cholera, Dengue, Diabetes, Ebola, HIV/AIDS, Hepatitis, Hypertension, Influenza, Leprosy, Malaria, Measles, Parkinson's Disease, Polio, Rabies, Tuberculosis, Zika
- **age_group** (4): 0-18, 19-35, 36-60, 61+
- **gender** (3): Female, Male, Other
- **treatment_type** (4): Medication, Surgery, Therapy, Vaccination
- **vaccine_treatment_available** (2): false, true

## Unmapped Disease Names

All disease names covered by DISEASE_CATEGORY_MAP.