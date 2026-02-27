from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipeline.config import DB_PATH, PROJECT_ROOT, REPORTS_DIR


@dataclass(frozen=True)
class Paths:
    project_root: Path = PROJECT_ROOT
    db_path: Path = DB_PATH
    reports_dir: Path = REPORTS_DIR


PATHS = Paths()


CORS_ORIGINS: tuple[str, ...] = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


MARKDOWN_ALLOWLIST: dict[str, Path] = {
    "data_quality_report": PATHS.reports_dir / "data_quality_report.md",
    "prompt_gap_matrix": PATHS.reports_dir / "prompt_gap_matrix.md",
}


KNOWN_ARTIFACTS: dict[str, Path] = {
    "run_metadata": PATHS.reports_dir / "_run_metadata.json",
    "assumption_log": PATHS.reports_dir / "assumption_log.csv",
    "data_quality_report": PATHS.reports_dir / "data_quality_report.md",
    "synthetic_signatures": PATHS.reports_dir / "synthetic_signatures.json",
    "prompt_gap_matrix": PATHS.reports_dir / "prompt_gap_matrix.md",
    "ml_diagnostic": PATHS.reports_dir / "ml_diagnostic.json",
    "summary_executive_html": PATHS.reports_dir / "summary_executive.html",
    "benchmark_comparison_html": PATHS.reports_dir / "benchmark_comparison.html",
    "q1_outcome_geography_html": PATHS.reports_dir / "q1_outcome_geography.html",
    "q2_access_vs_outcomes_html": PATHS.reports_dir / "q2_access_vs_outcomes.html",
    "q3_outlier_communities_html": PATHS.reports_dir / "q3_outlier_communities.html",
    "q4_sensitivity_tiers_html": PATHS.reports_dir / "q4_sensitivity_tiers.html",
    "q5_sparse_reporting_html": PATHS.reports_dir / "q5_sparse_reporting.html",
    "q6_premature_conclusions_html": PATHS.reports_dir / "q6_premature_conclusions.html",
}


METRIC_COLUMNS: tuple[str, ...] = (
    "mortality_rate",
    "recovery_rate",
    "dalys",
    "healthcare_access",
    "doctors_per_1000",
    "hospital_beds_per_1000",
    "avg_treatment_cost_usd",
    "per_capita_income",
    "education_index",
    "urbanization_rate",
    "resource_index",
    "access_composite",
    "access_outcome_gap",
    "cost_burden_ratio",
    "prevalence_rate",
    "incidence_rate",
    "improvement_in_5_years",
)

