# Data Quality Report
Generated: 2026-02-24T23:47:27.134350+00:00

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
| Tuberculosis | 11 | ['Autoimmune', 'Infectious', 'Bacterial', 'Neurological', 'Genetic', 'Respiratory', 'Metabolic', 'Parasitic', 'Viral', 'Chronic', 'Cardiovascular'] |
| Parkinson's Disease | 11 | ['Autoimmune', 'Infectious', 'Neurological', 'Bacterial', 'Metabolic', 'Genetic', 'Parasitic', 'Respiratory', 'Viral', 'Chronic', 'Cardiovascular'] |
| Ebola | 11 | ['Chronic', 'Cardiovascular', 'Viral', 'Genetic', 'Parasitic', 'Respiratory', 'Metabolic', 'Bacterial', 'Neurological', 'Infectious', 'Autoimmune'] |
| Malaria | 11 | ['Chronic', 'Viral', 'Cardiovascular', 'Respiratory', 'Parasitic', 'Metabolic', 'Genetic', 'Neurological', 'Bacterial', 'Infectious', 'Autoimmune'] |
| Cholera | 11 | ['Bacterial', 'Neurological', 'Autoimmune', 'Infectious', 'Viral', 'Chronic', 'Cardiovascular', 'Parasitic', 'Genetic', 'Respiratory', 'Metabolic'] |
| Leprosy | 11 | ['Bacterial', 'Neurological', 'Autoimmune', 'Infectious', 'Chronic', 'Cardiovascular', 'Viral', 'Respiratory', 'Parasitic', 'Metabolic', 'Genetic'] |
| COVID-19 | 11 | ['Neurological', 'Bacterial', 'Infectious', 'Autoimmune', 'Cardiovascular', 'Viral', 'Chronic', 'Metabolic', 'Genetic', 'Parasitic', 'Respiratory'] |
| Hypertension | 11 | ['Neurological', 'Bacterial', 'Infectious', 'Autoimmune', 'Viral', 'Cardiovascular', 'Chronic', 'Metabolic', 'Parasitic', 'Respiratory', 'Genetic'] |
| HIV/AIDS | 11 | ['Neurological', 'Bacterial', 'Infectious', 'Autoimmune', 'Chronic', 'Cardiovascular', 'Viral', 'Respiratory', 'Parasitic', 'Genetic', 'Metabolic'] |
| Alzheimer's Disease | 11 | ['Chronic', 'Viral', 'Cardiovascular', 'Genetic', 'Respiratory', 'Metabolic', 'Parasitic', 'Bacterial', 'Neurological', 'Autoimmune', 'Infectious'] |
| Influenza | 11 | ['Viral', 'Chronic', 'Cardiovascular', 'Genetic', 'Metabolic', 'Parasitic', 'Respiratory', 'Bacterial', 'Neurological', 'Autoimmune', 'Infectious'] |
| Hepatitis | 11 | ['Bacterial', 'Neurological', 'Infectious', 'Autoimmune', 'Viral', 'Cardiovascular', 'Chronic', 'Metabolic', 'Genetic', 'Respiratory', 'Parasitic'] |
| Asthma | 11 | ['Neurological', 'Bacterial', 'Autoimmune', 'Infectious', 'Cardiovascular', 'Chronic', 'Viral', 'Parasitic', 'Respiratory', 'Metabolic', 'Genetic'] |
| Zika | 11 | ['Respiratory', 'Genetic', 'Parasitic', 'Metabolic', 'Cardiovascular', 'Chronic', 'Viral', 'Infectious', 'Autoimmune', 'Neurological', 'Bacterial'] |
| Measles | 11 | ['Parasitic', 'Metabolic', 'Genetic', 'Respiratory', 'Cardiovascular', 'Viral', 'Chronic', 'Autoimmune', 'Infectious', 'Neurological', 'Bacterial'] |
| Rabies | 11 | ['Respiratory', 'Metabolic', 'Genetic', 'Parasitic', 'Chronic', 'Cardiovascular', 'Viral', 'Infectious', 'Autoimmune', 'Bacterial', 'Neurological'] |
| Dengue | 11 | ['Metabolic', 'Genetic', 'Respiratory', 'Parasitic', 'Cardiovascular', 'Viral', 'Chronic', 'Infectious', 'Autoimmune', 'Neurological', 'Bacterial'] |
| Polio | 11 | ['Neurological', 'Bacterial', 'Autoimmune', 'Infectious', 'Viral', 'Chronic', 'Cardiovascular', 'Respiratory', 'Genetic', 'Parasitic', 'Metabolic'] |
| Cancer | 11 | ['Chronic', 'Cardiovascular', 'Viral', 'Respiratory', 'Metabolic', 'Parasitic', 'Genetic', 'Neurological', 'Bacterial', 'Infectious', 'Autoimmune'] |
| Diabetes | 11 | ['Parasitic', 'Genetic', 'Metabolic', 'Respiratory', 'Cardiovascular', 'Viral', 'Chronic', 'Infectious', 'Autoimmune', 'Neurological', 'Bacterial'] |

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