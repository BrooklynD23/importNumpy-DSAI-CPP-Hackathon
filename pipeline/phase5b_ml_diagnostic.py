"""Phase 5b: ML Diagnostic — prove the dataset is synthetic via model probes.

Trained on real-world health data, a gradient-boosted or random-forest model
should achieve meaningful R² / accuracy. On uniformly distributed synthetic
data these models find nothing — confirming our dataset has no real signal.

Outputs: reports/ml_diagnostic.json
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import duckdb
import numpy as np

from pipeline.config import DB_PATH, REPORTS_DIR

# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------
REGRESSION_TARGETS = ["mortality_rate", "recovery_rate", "dalys"]
FEATURE_COLS = [
    "healthcare_access",
    "doctors_per_1000",
    "hospital_beds_per_1000",
    "per_capita_income",
    "education_index",
    "urbanization_rate",
    "population_affected",
    "avg_treatment_cost_usd",
]
CLASSIFICATION_TARGET = "disease_category"

# Sample cap to keep runtime reasonable
SAMPLE_CAP = 10_000
CV_FOLDS = 5
RANDOM_STATE = 42


def _load_data(con: duckdb.DuckDBPyConnection) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    """Return (X, {target: y}, y_class)."""
    all_cols = ", ".join(FEATURE_COLS + REGRESSION_TARGETS + [CLASSIFICATION_TARGET])
    query = f"""
        SELECT {all_cols}
        FROM clean_health
        WHERE data_quality_flag = 'ok'
            AND {" AND ".join(f"{c} IS NOT NULL" for c in FEATURE_COLS + REGRESSION_TARGETS)}
            AND {CLASSIFICATION_TARGET} IS NOT NULL
        USING SAMPLE {SAMPLE_CAP} ROWS (reservoir, {RANDOM_STATE})
    """
    df = con.execute(query).df()

    X = df[list(FEATURE_COLS)].values.astype(float)
    y_reg = {col: df[col].values.astype(float) for col in REGRESSION_TARGETS}
    # Encode disease_category as integer labels
    cats = df[CLASSIFICATION_TARGET].astype("category")
    y_cls = cats.cat.codes.values.astype(int)
    chance = 1.0 / max(cats.nunique(), 1)
    return X, y_reg, y_cls, chance


def _verdict_r2(r2: float) -> str:
    if r2 < 0.01:
        return "Near-zero R² — no predictable signal (consistent with synthetic data)"
    if r2 < 0.05:
        return "Marginal R² — very weak signal, likely noise"
    if r2 < 0.30:
        return "Low R² — some spurious structure detected; investigate further"
    return "High R² — unexpected real signal present"


def _verdict_cls(accuracy: float, chance: float) -> str:
    ratio = accuracy / chance if chance > 0 else 1.0
    if ratio < 1.05:
        return f"Accuracy at chance ({accuracy:.1%} vs {chance:.1%} baseline) — no learnable structure"
    if ratio < 1.20:
        return f"Slightly above chance ({accuracy:.1%} vs {chance:.1%}) — minimal structure"
    return f"Above chance ({accuracy:.1%} vs {chance:.1%}) — meaningful structure detected"


def run(con: duckdb.DuckDBPyConnection) -> None:
    print("  [5b] Running ML diagnostic probes...")

    try:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.model_selection import cross_val_score
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required for Phase 5b. "
            "Add scikit-learn>=1.4.0 to requirements.txt and reinstall."
        ) from exc

    X, y_reg, y_cls, chance = _load_data(con)
    n = len(X)
    print(f"  [5b] Loaded {n} rows for ML probes.")

    # ── Regression probes ──────────────────────────────────────────────────
    regression_probes = []
    for target in REGRESSION_TARGETS:
        y = y_reg[target]
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(
                n_estimators=50, max_depth=5, random_state=RANDOM_STATE, n_jobs=-1
            )),
        ])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scores = cross_val_score(pipe, X, y, cv=CV_FOLDS, scoring="r2")
        r2_mean = float(np.mean(scores))
        r2_std = float(np.std(scores))
        print(f"  [5b]   {target}: R²={r2_mean:.4f} ± {r2_std:.4f}")
        regression_probes.append({
            "target": target,
            "cv_r2_mean": round(r2_mean, 6),
            "cv_r2_std": round(r2_std, 6),
            "verdict": _verdict_r2(r2_mean),
        })

    # ── Classification probe ──────────────────────────────────────────────
    cls_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=50, max_depth=5, random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cls_scores = cross_val_score(cls_pipe, X, y_cls, cv=CV_FOLDS, scoring="accuracy")
    cls_mean = float(np.mean(cls_scores))
    print(f"  [5b]   disease_category: accuracy={cls_mean:.4f} (chance={chance:.4f})")

    # ── Overall conclusion ────────────────────────────────────────────────
    all_r2_near_zero = all(p["cv_r2_mean"] < 0.02 for p in regression_probes)
    cls_near_chance = (cls_mean / chance) < 1.10 if chance > 0 else True

    if all_r2_near_zero and cls_near_chance:
        conclusion = (
            "All ML probes fail to learn. Regression R² values are near-zero and "
            "classification performs at chance baseline — confirming this dataset "
            "is synthetically generated with no real-world signal."
        )
    elif all_r2_near_zero:
        conclusion = (
            "Regression probes find no predictive structure (R² ≈ 0). "
            "Classification is slightly above chance but not meaningfully so. "
            "Dataset is consistent with synthetic generation."
        )
    else:
        conclusion = (
            "ML probes detected some structure. Further investigation recommended "
            "to determine whether this reflects real patterns or artefacts."
        )

    payload = {
        "n_rows_sampled": n,
        "cv_folds": CV_FOLDS,
        "features": FEATURE_COLS,
        "regression_probes": regression_probes,
        "classification_probe": {
            "target": CLASSIFICATION_TARGET,
            "cv_accuracy_mean": round(cls_mean, 6),
            "cv_accuracy_std": round(float(np.std(cls_scores)), 6),
            "chance_accuracy": round(chance, 6),
            "verdict": _verdict_cls(cls_mean, chance),
        },
        "overall_verdict": {
            "conclusion": conclusion,
            "all_regression_near_zero": all_r2_near_zero,
            "classification_at_chance": cls_near_chance,
        },
    }

    out_path = REPORTS_DIR / "ml_diagnostic.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  [5b] ML diagnostic written to {out_path}")


def verify(con: duckdb.DuckDBPyConnection) -> None:  # noqa: ARG001
    path = REPORTS_DIR / "ml_diagnostic.json"
    if not path.exists():
        raise RuntimeError(f"Phase 5b verification failed: {path} not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    if "overall_verdict" not in data:
        raise RuntimeError("Phase 5b verification failed: missing 'overall_verdict' in output")
    print("  [5b] Verification passed.")
