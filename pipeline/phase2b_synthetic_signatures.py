"""Phase 2b: Synthetic-signature extraction — reads raw_health, writes JSON metrics.

Purpose
-------
Phase 2 (phase2_profile.py) answers: "Is the data clean and within expected bounds?"
This phase answers: "Does the dataset exhibit structural signatures consistent with
synthetic or heavily synthetic-balanced generation?"

Outputs
-------
- reports/synthetic_signatures.json

This file is machine-readable so notebooks can auto-inject consistent "data reality"
badges without recomputing expensive diagnostics.
"""

from __future__ import annotations

import json
import math

import duckdb
import numpy as np
from scipy.stats import chi2_contingency

from pipeline.config import PROJECT_ROOT, RATE_COLUMNS, RAW_CSV, REPORTS_DIR


_CORR_NUMERIC_COLUMNS: tuple[str, ...] = (
    "prevalence_rate",
    "incidence_rate",
    "mortality_rate",
    "population_affected",
    "healthcare_access",
    "doctors_per_1000",
    "hospital_beds_per_1000",
    "avg_treatment_cost_usd",
    "recovery_rate",
    "dalys",
    "improvement_in_5_years",
    "per_capita_income",
    "education_index",
    "urbanization_rate",
)

_QUANTIZATION_DOUBLE_COLUMNS: tuple[str, ...] = tuple(
    c for c in _CORR_NUMERIC_COLUMNS if c != "population_affected"
)


def _safe_float(x: object) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _compute_entropy(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return 0.0
    p = counts / total
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _stabilize_json(obj: object, *, round_decimals: int = 10) -> object:
    """Recursively stabilize numeric output to avoid run-to-run float jitter.

    DuckDB aggregates on large tables can show tiny floating-point differences across runs
    (thread scheduling, vectorization). We round floats to a fixed precision so judge-facing
    artifacts stay diff-stable when the underlying data/code is unchanged.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, round_decimals)
    if isinstance(obj, dict):
        return {k: _stabilize_json(v, round_decimals=round_decimals) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stabilize_json(v, round_decimals=round_decimals) for v in obj]
    return obj


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Write synthetic-signature metrics to reports/synthetic_signatures.json."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        dataset_path = str(RAW_CSV.relative_to(PROJECT_ROOT))
    except ValueError:
        dataset_path = str(RAW_CSV)

    # ── 1) Structural coverage + duplicate-per-cell distribution ─────────────
    dim_stats = con.execute("""
        SELECT
            COUNT(*) AS n_rows,
            COUNT(DISTINCT country) AS n_country,
            COUNT(DISTINCT year) AS n_year,
            COUNT(DISTINCT disease_name) AS n_disease,
            COUNT(DISTINCT age_group) AS n_age_group,
            COUNT(DISTINCT gender) AS n_gender
        FROM raw_health
    """).fetchone()
    n_rows = int(dim_stats[0])
    dims = {
        "country": int(dim_stats[1]),
        "year": int(dim_stats[2]),
        "disease_name": int(dim_stats[3]),
        "age_group": int(dim_stats[4]),
        "gender": int(dim_stats[5]),
    }
    max_combos = int(
        dims["country"]
        * dims["year"]
        * dims["disease_name"]
        * dims["age_group"]
        * dims["gender"]
    )

    observed_combos = int(con.execute("""
        SELECT COUNT(*) FROM (
            SELECT 1
            FROM raw_health
            GROUP BY country, year, disease_name, age_group, gender
        )
    """).fetchone()[0])

    duplicate_groups = int(con.execute("""
        SELECT COUNT(*) FROM (
            SELECT 1
            FROM raw_health
            GROUP BY country, year, disease_name, age_group, gender
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0])

    cell_dist = con.execute("""
        SELECT
            MIN(n) AS min_n,
            approx_quantile(n, 0.50) AS p50_n,
            approx_quantile(n, 0.95) AS p95_n,
            MAX(n) AS max_n,
            AVG(n) AS mean_n,
            STDDEV_SAMP(n) AS sd_n
        FROM (
            SELECT COUNT(*) AS n
            FROM raw_health
            GROUP BY country, year, disease_name, age_group, gender
        )
    """).fetchone()

    # ── 2) Quantization: % values equal to ROUND(x, 2) ───────────────────────
    quant_exprs = [
        (
            f"SUM(CASE WHEN ABS({c} - ROUND({c}, 2)) < 1e-9 THEN 1 ELSE 0 END) "
            f"AS {c}__n_2dp"
        )
        for c in _QUANTIZATION_DOUBLE_COLUMNS
    ]
    quant_sql = (
        "SELECT COUNT(*) AS n_rows, "
        + ", ".join(quant_exprs)
        + " FROM raw_health"
    )
    quant_row = con.execute(quant_sql).fetchone()
    quant_total = int(quant_row[0])
    quantization = {}
    for idx, col in enumerate(_QUANTIZATION_DOUBLE_COLUMNS, start=1):
        n_2dp = int(quant_row[idx])
        quantization[col] = {
            "pct_2dp": n_2dp / quant_total if quant_total else None,
            "n_non_2dp": quant_total - n_2dp,
        }

    # ── 3) Correlations (all pairs, single scan) ──────────────────────────────
    corr_cols = list(_CORR_NUMERIC_COLUMNS)
    corr_exprs = []
    pair_names: list[tuple[str, str, str]] = []
    for i in range(len(corr_cols)):
        for j in range(i + 1, len(corr_cols)):
            a, b = corr_cols[i], corr_cols[j]
            alias = f"corr__{a}__{b}"
            corr_exprs.append(f"CORR({a}, {b}) AS {alias}")
            pair_names.append((a, b, alias))
    corr_sql = "SELECT " + ", ".join(corr_exprs) + " FROM raw_health"
    corr_vals = con.execute(corr_sql).fetchone()
    corrs: dict[str, float | None] = {}
    for (a, b, alias), val in zip(pair_names, corr_vals, strict=True):
        corrs[f"{a}__{b}"] = _safe_float(val)

    # Determine max |r| and top pairs by |r|
    corr_items = [
        (k, v) for k, v in corrs.items() if v is not None and not math.isnan(v)
    ]
    corr_items_sorted = sorted(corr_items, key=lambda kv: abs(kv[1]), reverse=True)
    max_abs_corr = abs(corr_items_sorted[0][1]) if corr_items_sorted else None
    top_corr_pairs = [
        {"pair": k, "r": v, "abs_r": abs(v)}
        for k, v in corr_items_sorted[:10]
    ]

    # Domain-critical subset (explicit keys for stable downstream rendering)
    def _corr_key(a: str, b: str) -> str:
        return f"{a}__{b}" if f"{a}__{b}" in corrs else f"{b}__{a}"

    domain_corrs = {
        "access__mortality": corrs.get(_corr_key("healthcare_access", "mortality_rate")),
        "access__recovery": corrs.get(_corr_key("healthcare_access", "recovery_rate")),
        "income__access": corrs.get(_corr_key("per_capita_income", "healthcare_access")),
        "income__mortality": corrs.get(_corr_key("per_capita_income", "mortality_rate")),
        "education__access": corrs.get(_corr_key("education_index", "healthcare_access")),
        "education__mortality": corrs.get(_corr_key("education_index", "mortality_rate")),
        "urbanization__access": corrs.get(_corr_key("urbanization_rate", "healthcare_access")),
    }

    # ── 4) Uniform-range sanity for bounded columns ───────────────────────────
    bounded_cols = list(RATE_COLUMNS)
    bounded_exprs = []
    for c in bounded_cols:
        bounded_exprs.extend(
            [
                f"MIN({c}) AS {c}__min",
                f"MAX({c}) AS {c}__max",
                f"AVG({c}) AS {c}__mean",
                f"STDDEV_SAMP({c}) AS {c}__sd",
            ]
        )
    bounded_sql = "SELECT " + ", ".join(bounded_exprs) + " FROM raw_health"
    bounded_row = con.execute(bounded_sql).fetchone()
    uniform_checks: dict[str, dict[str, float | None]] = {}
    k = 0
    for c in bounded_cols:
        obs_min = _safe_float(bounded_row[k])
        obs_max = _safe_float(bounded_row[k + 1])
        obs_mean = _safe_float(bounded_row[k + 2])
        obs_sd = _safe_float(bounded_row[k + 3])
        k += 4
        if obs_min is None or obs_max is None:
            uniform_checks[c] = {"observed": None, "expected_uniform": None}
            continue
        exp_mean = (obs_min + obs_max) / 2.0
        exp_sd = (obs_max - obs_min) / math.sqrt(12.0)
        uniform_checks[c] = {
            "observed": {
                "min": obs_min,
                "max": obs_max,
                "mean": obs_mean,
                "sd": obs_sd,
            },
            "expected_uniform": {
                "mean": exp_mean,
                "sd": exp_sd,
            },
            "abs_error": {
                "mean": None if obs_mean is None else abs(obs_mean - exp_mean),
                "sd": None if obs_sd is None else abs(obs_sd - exp_sd),
            },
        }

    # ── 5) Label reliability: disease_name × disease_category_original ─────────
    cats = con.execute("""
        SELECT disease_name, disease_category_original, COUNT(*) AS n
        FROM raw_health
        GROUP BY disease_name, disease_category_original
    """).fetchall()

    diseases = sorted({r[0] for r in cats})
    categories = sorted({r[1] for r in cats})
    disease_index = {d: i for i, d in enumerate(diseases)}
    category_index = {c: i for i, c in enumerate(categories)}
    table = np.zeros((len(diseases), len(categories)), dtype=float)
    for disease, category, n in cats:
        table[disease_index[disease], category_index[category]] = float(n)

    # Entropy per disease (within-row distribution)
    entropies = []
    for i, disease in enumerate(diseases):
        ent = _compute_entropy(table[i, :])
        entropies.append(ent)
    mean_entropy = float(np.mean(entropies)) if entropies else None
    max_entropy = float(math.log2(len(categories))) if categories else None
    entropy_gap = None
    if mean_entropy is not None and max_entropy is not None:
        entropy_gap = max_entropy - mean_entropy

    # Independence test + Cramer's V (contingency table is small)
    chi2, p_value, dof, _expected = chi2_contingency(table, correction=False)
    n_total = float(table.sum())
    min_dim = min(table.shape[0] - 1, table.shape[1] - 1)
    cramer_v = float(math.sqrt(chi2 / (n_total * min_dim))) if n_total > 0 and min_dim > 0 else None

    # Categories-per-disease summary
    cats_per_disease = con.execute("""
        SELECT
            MIN(n_cats) AS min_n_cats,
            AVG(n_cats) AS mean_n_cats,
            MAX(n_cats) AS max_n_cats
        FROM (
            SELECT disease_name, COUNT(DISTINCT disease_category_original) AS n_cats
            FROM raw_health
            GROUP BY disease_name
        )
    """).fetchone()

    label_reliability = {
        "n_diseases": len(diseases),
        "n_categories": len(categories),
        "categories_per_disease": {
            "min": int(cats_per_disease[0]) if cats_per_disease[0] is not None else None,
            "mean": _safe_float(cats_per_disease[1]),
            "max": int(cats_per_disease[2]) if cats_per_disease[2] is not None else None,
        },
        "entropy_by_disease": {
            "mean": mean_entropy,
            "max_possible": max_entropy,
            "gap_to_max": entropy_gap,
        },
        "independence": {
            "chi2": float(chi2),
            "dof": int(dof),
            "p_value": float(p_value),
            "cramers_v": cramer_v,
        },
    }

    payload = {
        "schema_version": 1,
        "dataset_path": dataset_path,
        "table": "raw_health",
        "n_rows": n_rows,
        "dimensions": dims,
        "combination_coverage": {
            "max_possible": max_combos,
            "observed": observed_combos,
            "coverage_rate": observed_combos / max_combos if max_combos else None,
        },
        "duplicate_groups": {
            "count_groups_with_n_gt_1": duplicate_groups,
            "cell_n_distribution": {
                "min": int(cell_dist[0]) if cell_dist[0] is not None else None,
                "p50": int(cell_dist[1]) if cell_dist[1] is not None else None,
                "p95": int(cell_dist[2]) if cell_dist[2] is not None else None,
                "max": int(cell_dist[3]) if cell_dist[3] is not None else None,
                "mean": _safe_float(cell_dist[4]),
                "sd": _safe_float(cell_dist[5]),
            },
        },
        "quantization": {
            "definition": "pct of values where ABS(x - ROUND(x,2)) < 1e-9",
            "per_column": quantization,
        },
        "correlation_scan": {
            "numeric_columns": list(_CORR_NUMERIC_COLUMNS),
            "max_abs_corr": max_abs_corr,
            "top_pairs_by_abs_r": top_corr_pairs,
            "domain_critical": domain_corrs,
        },
        "bounded_uniform_checks": {
            "definition": "Compare observed mean/sd to Uniform(min,max) expectation (descriptive sanity check).",
            "per_column": uniform_checks,
        },
        "label_reliability": label_reliability,
    }

    out_path = REPORTS_DIR / "synthetic_signatures.json"
    stable_payload = _stabilize_json(payload)
    out_path.write_text(
        json.dumps(stable_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"  Synthetic signatures written to {out_path}")


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Verify synthetic_signatures.json exists and contains required keys."""
    out_path = REPORTS_DIR / "synthetic_signatures.json"
    assert out_path.exists(), f"Missing {out_path}"
    raw = out_path.read_text(encoding="utf-8")
    data = json.loads(raw)

    for key in (
        "schema_version",
        "n_rows",
        "dimensions",
        "combination_coverage",
        "quantization",
        "correlation_scan",
        "label_reliability",
    ):
        assert key in data, f"Missing key in synthetic_signatures.json: {key}"

    assert data["schema_version"] == 1, f"Unexpected schema_version: {data['schema_version']}"

    cov = data["combination_coverage"].get("coverage_rate")
    assert cov is None or (0.0 <= cov <= 1.0), f"Invalid coverage_rate: {cov}"

    q = data["quantization"]["per_column"]
    assert isinstance(q, dict) and q, "quantization.per_column is empty"

    print("  Synthetic signatures verified — OK")
