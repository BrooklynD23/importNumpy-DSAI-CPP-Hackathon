# Pipeline Technical Reference

**Team importNumpy** | DND Spring 2026 Datathon

---

## Architecture Overview

```
Raw Dataset/Global Health Statistics.csv   (1,000,000 rows × 25 columns, read-only)
        │
        ▼
pipeline/phase1_ingest.py   → DuckDB table: raw_health
        │
        ▼
pipeline/phase2_profile.py  → reports/data_quality_report.md
                              reports/assumption_log.csv
        │
        ▼
pipeline/phase2b_synthetic_signatures.py → reports/synthetic_signatures.json
        │
        ▼
pipeline/phase3_clean.py    → DuckDB table: clean_health
                              DuckDB table: country_summary
        │
        ▼
pipeline/phase4_views.py    → DuckDB tables: v_outcome_by_geography
                                             v_access_vs_outcomes
                                             v_outlier_communities
                                             v_sensitivity_tiers
                                             v_sparse_reporting
                                             v_premature_conclusions
        │
        ▼
pipeline/phase4b_robust_views.py → DuckDB table: cell_health
                                  DuckDB tables: v_*_dedup
                                  DuckDB table: robustness_delta_summary
        │
        ▼
pipeline/phase5_prompt_gap_matrix.py → reports/prompt_gap_matrix.md
        │
        ▼
nbconvert --execute (8 notebooks) → reports/*.html
                                    reports/figures/*.png (30 figures)
```

All state lives in `data/health.duckdb`. No intermediate CSVs. No pandas for transforms — DuckDB SQL only, for reproducibility and performance.

---

## Phase 1: Ingest (`pipeline/phase1_ingest.py`)

**Input:** `Raw Dataset/Global Health Statistics.csv`
**Output:** `raw_health` table (DuckDB)

Steps:
1. Read CSV with DuckDB's native CSV reader (type inference enabled)
2. Normalise column names to snake_case
3. Create `urbanization_tier` (default 3-tier scheme, from `urbanization_rate`)
4. Compute `resource_index` (simple supply proxy from doctors + beds)

**Verification gate:** asserts 1,000,000 rows, 25 columns, 3 distinct tiers.

---

## Phase 2: Data Quality Profiling (`pipeline/phase2_profile.py`)

**Input:** `raw_health`
**Output:** `reports/data_quality_report.md`, `reports/assumption_log.csv`

Checks performed:
- Missingness rate per column (flag threshold: >5%)
- Out-of-range values for rate columns (valid: 0–100%)
- Duplicate-group detection at `(country, year, disease, age, gender)` grain
- Disease-name coverage against `DISEASE_CATEGORY_MAP` (unmapped check)

Assumption log records each data decision made (5 entries), preserving an audit trail for judges.

---

## Phase 2b: Synthetic Signatures (`pipeline/phase2b_synthetic_signatures.py`)

**Input:** `raw_health`  
**Output:** `reports/synthetic_signatures.json`

This phase consolidates the headline “synthetic / low-signal” diagnostics into a **machine-readable**
artifact so notebooks and the executive summary can render consistent “data reality” badges without
recomputing expensive scans.

Includes (high level):
- Combination coverage rate (near-Cartesian design check)
- Duplicate-per-cell distribution summary
- Quantization check (pct values consistent with 2-decimal rounding)
- Correlation scan (max |r| and key domain pairs)
- Label reliability (entropy + independence for `disease_name × disease_category_original`)

---

## Phase 3: Clean & Transform (`pipeline/phase3_clean.py`)

**Input:** `raw_health`
**Output:** `clean_health` table, `country_summary` table

**Immutability rule:** `raw_health` is never modified. `clean_health` is a derived copy filtered to `data_quality_flag = 'ok'` rows. With this dataset, all 1M rows pass (100% ok), which itself is evidence of synthetic generation (real data always has some noise).

`country_summary` aggregates to 20-row country-level means for quick lookup.

---

## Phase 4: Analytical Views (`pipeline/phase4_views.py`)

Six materialized tables — one per competition question. All enforce `SMALL_N_THRESHOLD = 30` (groups with fewer than 30 observations are excluded from analytical views).

| Table | Grain | Key Columns | Used By |
|-------|-------|-------------|---------|
| `v_outcome_by_geography` | country × tier × disease | avg/sd mortality, recovery, DALYs | Q1 |
| `v_access_vs_outcomes` | country × tier × age_group | avg access, CORR(access, mortality) | Q2 |
| `v_outlier_communities` | country | z_access, z_mortality, outlier_type | Q3 |
| `v_sensitivity_tiers` | tier_scheme × tier_label | avg_mortality per scheme | Q4 |
| `v_sparse_reporting` | country × disease × age_group | n, ci_half_width, sample_adequacy | Q5 |
| `v_premature_conclusions` | disease × tier | CORR() pairs for all variable combinations | Q6 |

**Verification gate:** asserts all 6 tables are non-empty and `v_sensitivity_tiers` has exactly 3 schemes.

---

## Phase 4b: Robustness (Dedup-at-Cell Views) (`pipeline/phase4b_robust_views.py`)

**Input:** `clean_health` + Phase 4 base tables  
**Outputs:** `cell_health`, `v_*_dedup`, `robustness_delta_summary`

This phase addresses a core structural limitation: repeated observations per structural cell. It
creates a deduped table (`cell_health`) that aggregates repeated observations **while preserving the
tier labels used in analysis** (so robustness checks do not accidentally collapse the tier
distribution via averaging artifacts), then rebuilds the six analytical views from that table.

`robustness_delta_summary` is a compact join-based delta table that notebooks query for a lightweight
“base vs dedup” check.

---

## Phase 5: Prompt Gap Matrix (`pipeline/phase5_prompt_gap_matrix.py`)

**Input:** `DatathonHostPrompt.md` (repo file)  
**Output:** `reports/prompt_gap_matrix.md`

This report documents where the prompt asks for concepts not measured in the dataset (e.g.,
distance-to-care, utilization) and what proxies we use instead. It is primarily a judge-defense
artifact.

---

## Notebooks

All notebooks follow the same pattern:
1. `sys.path.insert(0, '..')` to resolve `notebooks._helpers`
2. `set_plot_style()` + `get_connection()` from `_helpers.py`
3. SQL queries via `con.execute().fetchdf()`
4. Figures saved via `save_fig(fig, name)` → `reports/figures/{name}.png` + `.svg`
5. `con.close()` at end

### `_helpers.py` — Shared Utilities

| Symbol | Type | Purpose |
|--------|------|---------|
| `DB_PATH` | `Path` | Absolute path to `data/health.duckdb` |
| `FIGURES_DIR` | `Path` | `reports/figures/` (auto-created) |
| `TIER_COLORS` | `dict` | Color map: Rural=green, Peri-urban=orange, Urban=red |
| `get_connection()` | fn | Read-only DuckDB connection |
| `set_plot_style()` | fn | seaborn whitegrid + rcParams (300dpi, consistent fonts) |
| `save_fig(fig, name)` | fn | Saves PNG (300dpi) + SVG to `FIGURES_DIR` |
| `effect_size_label(d)` | fn | negligible / small / medium / large |
| `format_ci(mean, ci)` | fn | "X.XX% [lo, hi]" string formatter |
| `load_synthetic_signatures()` | fn | Loads `reports/synthetic_signatures.json` |
| `get_robustness_delta(con, view_name)` | fn | Fetches row from `robustness_delta_summary` |

---

## Benchmark Comparison Notebook (`notebooks/benchmark_comparison.ipynb`)

This notebook is **read-only with respect to DuckDB** — it never writes to the database. All benchmark data is generated in-memory using:

```python
rng = np.random.default_rng(seed=2026)
```

### Latent-Factor Generation

A single "development" score `dev_factor ~ N(0,1)` drives all country-level variables, ensuring realistic correlations emerge naturally:

```
access_mean  = clip(55 + 20*dev + noise, 15, 95)
mortality    = clip(9  - 2.5*dev + noise, 1.5, 18)
income       = clip(12000 + 8000*dev + noise, 800, 45000)
```

This produces r(access, mortality) ≈ –0.45 to –0.67, matching WHO cross-national literature.

Two "outlier" countries are manually injected (low income, low mortality) to simulate Cuba-like public-health-system anomalies.

### Figure Naming Convention

All benchmark figures are prefixed `bench_` to distinguish from per-question figures:

```
bench_q{N}_{description}.png   — Q1–Q6 side-by-side comparisons
bench_data_readiness_scorecard  — 8×3 traffic-light grid
bench_action_timeline           — Swim-lane Gantt, 30/60/90 days
```

---

## Execution Order and Dependencies

```
run.sh
  ├── venv setup
  ├── pip install -r requirements.txt
  ├── python -m pipeline.run_pipeline     # Phases 1–5 (sequential, gated)
  └── for nb in q1 q2 q3 q4 q5 q6 benchmark_comparison summary_executive:
        jupyter nbconvert --execute notebooks/${nb}.ipynb \
          --to html --output-dir=reports/ \
          --ExecutePreprocessor.timeout=300

Optionally (default on local): `run.sh` can start a local dashboard server after the pipeline.
Set `RUN_DASHBOARD=0` to skip.
```

`benchmark_comparison` must run before `summary_executive` because the executive summary references benchmark figure filenames (though it does not re-generate them).

---

## Key Configuration (`pipeline/config.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SMALL_N_THRESHOLD` | 30 | Minimum group size for analytical views |
| `MISSINGNESS_FLAG_THRESHOLD` | 0.05 | Flag columns with >5% missing |
| `URBANIZATION_TIERS_DEFAULT` | Rural 0–30%, Peri-urban 30–70%, Urban 70–100% | Default 3-tier scheme |
| `URBANIZATION_TIERS_ALT1` | Rural 0–40%, Urban 40–100% | Binary scheme (sensitivity) |
| `URBANIZATION_TIERS_ALT2` | Rural / Peri-urban / Semi-urban / Urban (quartiles) | 4-tier scheme (sensitivity) |
| `DISEASE_CATEGORY_MAP` | 20-entry dict | Hand-curated replacement for unreliable CSV category |

---

## Outputs Produced by `bash run.sh`

| Path | Description |
|------|-------------|
| `data/health.duckdb` | Full analytical database |
| `reports/data_quality_report.md` | Phase 2 quality audit |
| `reports/assumption_log.csv` | Audit trail of data decisions |
| `reports/synthetic_signatures.json` | Phase 2b machine-readable synthetic metrics |
| `reports/prompt_gap_matrix.md` | Phase 5 prompt measurement gaps + proxy mapping |
| `reports/q1_outcome_geography.html` | Q1 full notebook output |
| `reports/q2_access_vs_outcomes.html` | Q2 full notebook output |
| `reports/q3_outlier_communities.html` | Q3 full notebook output |
| `reports/q4_sensitivity_tiers.html` | Q4 full notebook output |
| `reports/q5_sparse_reporting.html` | Q5 full notebook output |
| `reports/q6_premature_conclusions.html` | Q6 full notebook output |
| `reports/benchmark_comparison.html` | Dual-track benchmark notebook |
| `reports/summary_executive.html` | Executive synthesis dashboard |
| `reports/figures/*.png` | 30 figures (300dpi) |
| `reports/figures/*.svg` | 30 figures (vector, for presentations) |

---

## Design Decisions

**Why DuckDB over pandas for transforms?**
DuckDB's SQL is declarative, reproducible, and auditable. Pandas operations can silently mutate DataFrames (violating immutability). DuckDB also handles 1M rows comfortably in memory with no chunking required.

**Why materialized tables instead of views?**
The pipeline's phase4 tables are technically `CREATE TABLE AS SELECT`, not SQL `VIEW`. This means query results are cached and execution time for notebooks is fast (milliseconds vs seconds for recomputation).

**Why seed=2026 for benchmark generation?**
Reproducibility. Any reviewer running `bash run.sh` on any machine gets identical benchmark figures.

**Why SVG + PNG?**
PNG for inclusion in HTML reports (fast to render). SVG for presentation slides — vector graphics scale without pixelation at any resolution.
