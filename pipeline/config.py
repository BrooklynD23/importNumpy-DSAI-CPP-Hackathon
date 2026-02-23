"""Pipeline configuration: paths, column groups, mappings, thresholds."""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "Raw Dataset" / "Global Health Statistics.csv"
DB_PATH = PROJECT_ROOT / "data" / "health.duckdb"
REPORTS_DIR = PROJECT_ROOT / "reports"

# ── Column Groups ─────────────────────────────────────────────────────────────
RATE_COLUMNS = (
    "prevalence_rate",
    "incidence_rate",
    "mortality_rate",
    "recovery_rate",
    "improvement_in_5_years",
    "healthcare_access",
    "urbanization_rate",
)

OUTCOME_COLUMNS = (
    "mortality_rate",
    "recovery_rate",
    "dalys",
)

ACCESS_COLUMNS = (
    "healthcare_access",
    "doctors_per_1000",
    "hospital_beds_per_1000",
)

SOCIOECONOMIC_COLUMNS = (
    "per_capita_income",
    "education_index",
    "urbanization_rate",
)

# ── Disease Category Map ──────────────────────────────────────────────────────
# The original Disease Category column is unreliable (e.g. Malaria tagged as
# "Respiratory"). This hand-curated mapping replaces it entirely.
DISEASE_CATEGORY_MAP: dict[str, str] = {
    "Alzheimer's Disease": "Neurological",
    "Asthma": "Respiratory",
    "COVID-19": "Viral",
    "Cancer": "Oncological",
    "Cholera": "Bacterial",
    "Dengue": "Viral",
    "Diabetes": "Metabolic",
    "Ebola": "Viral",
    "HIV/AIDS": "Viral",
    "Hepatitis": "Viral",
    "Hypertension": "Cardiovascular",
    "Influenza": "Viral",
    "Leprosy": "Bacterial",
    "Malaria": "Parasitic",
    "Measles": "Viral",
    "Parkinson's Disease": "Neurological",
    "Polio": "Viral",
    "Rabies": "Viral",
    "Tuberculosis": "Bacterial",
    "Zika": "Viral",
}

# ── Urbanization Tier Schemes ─────────────────────────────────────────────────
# Default 3-tier for main analysis
URBANIZATION_TIERS_DEFAULT = {
    "Rural": (0, 30),
    "Peri-urban": (30, 70),
    "Urban": (70, 100.01),
}

# Alt1: binary split for sensitivity analysis (Question 4)
URBANIZATION_TIERS_ALT1 = {
    "Rural": (0, 40),
    "Urban": (40, 100.01),
}

# Alt2: 4-tier for sensitivity analysis (Question 4)
URBANIZATION_TIERS_ALT2 = {
    "Rural": (0, 25),
    "Peri-urban": (25, 50),
    "Semi-urban": (50, 75),
    "Urban": (75, 100.01),
}

# ── Thresholds ────────────────────────────────────────────────────────────────
SMALL_N_THRESHOLD = 30
MISSINGNESS_FLAG_THRESHOLD = 0.05
