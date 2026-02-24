# Phase 5: EDA & Insight Generation — Jupyter Notebooks

## Context

The DuckDB pipeline (Phases 1-4) is complete with 6 analytical views. The data quality report reveals the dataset is **synthetically generated** — near-zero correlations, uniform outcomes across geographies, identical country profiles. The next phase creates Jupyter notebooks that answer each competition question with honest analysis, turning the synthetic-data finding into a competitive advantage for Q5/Q6.

---

## Key Data Findings Driving This Plan

- **Zero missingness**, zero out-of-range values, 100% `ok` quality flags
- Mortality ~5.05% ± 0.02pp across ALL tiers/countries — negligible disparity
- Access↔mortality correlation r ≈ 0.0005 — no relationship
- All 20 countries within 0.1% of each other on all metrics
- All 24 confounder checks = "no_strong_confounder"
- All 640 sparse-reporting groups = "adequate"

---

## Files to Create

```
notebooks/
  _helpers.py                         # Shared: DuckDB conn, plot style, figure export
  q1_outcome_geography.ipynb          # Q1: Outcome disparities
  q2_access_vs_outcomes.ipynb         # Q2: Access vs outcomes
  q3_outlier_communities.ipynb        # Q3: Communities defying assumptions
  q4_sensitivity_tiers.ipynb          # Q4: Sensitivity to tier definitions
  q5_sparse_reporting.ipynb           # Q5: Uncertainty & sparse reporting
  q6_premature_conclusions.ipynb      # Q6: Premature conclusions
  summary_executive.ipynb             # Synthesis + presentation figures
reports/figures/                      # Generated PNG/SVG (gitignored)
```

---

## `notebooks/_helpers.py` — Shared Utilities

- `get_connection()` → read-only DuckDB connection via `pipeline.config.DB_PATH`
- `set_plot_style()` → seaborn `whitegrid`, consistent palette, publication fonts
- `save_fig(fig, name)` → saves to `reports/figures/{name}.png` (300dpi) + `.svg`
- `effect_size_label(d)` → Cohen's d → "negligible/small/medium/large"
- `format_ci(mean, ci_half)` → "5.05% [4.98, 5.12]"
- Color constants: `COLOR_RURAL`, `COLOR_PERIURBAN`, `COLOR_URBAN`

---

## Notebook Details

### Q1: Outcome Disparities (`q1_outcome_geography.ipynb`)
**Source:** `v_outcome_by_geography`, `clean_health`

| Analysis | Method |
|----------|--------|
| Tier comparison | Cohen's d between Rural/Peri-urban/Urban |
| Variance explained | One-way ANOVA → eta-squared (not p-values) |
| By disease category | Two-way groupby, within-category tier spreads |
| By country | Heatmap of country × tier mortality |

**Visualizations (4):**
1. Grouped bar chart — avg_mortality by tier with 95% CI error bars
2. Heatmap — 20 countries × 3 tiers, cell = avg_mortality
3. Violin plot — mortality distribution by tier
4. Effect size dot plot — Cohen's d for each tier pair, reference lines at 0.2/0.5

**Narrative:** Disparities are consistently ABSENT (d < 0.01).

---

### Q2: Access vs Outcomes (`q2_access_vs_outcomes.ipynb`)
**Source:** `v_access_vs_outcomes`, `clean_health` (10K sample for scatter)

| Analysis | Method |
|----------|--------|
| Correlation | Pearson/Spearman on access ↔ mortality/recovery |
| Regression | OLS fit, report R² |
| Threshold effects | Decile binning of healthcare_access |
| By subgroup | Per-group correlations from view |

**Visualizations (4):**
1. Scatter + regression line — access (x) vs mortality (y), with confidence band
2. Correlation histogram — distribution of per-group r values centered at 0
3. Decile step chart — mean mortality per access decile (flat line)
4. Faceted scatter — by urbanization tier (3 panels)

**Narrative:** R² < 0.001 — no access-outcome relationship. This ITSELF is a finding.

---

### Q3: Outlier Communities (`q3_outlier_communities.ipynb`)
**Source:** `v_outlier_communities`, `country_summary`

| Analysis | Method |
|----------|--------|
| Z-score analysis | All 20 countries, focus Russia (z=+2.5) and Turkey (z=+1.87) |
| Relaxed threshold | Re-classify at z > 0.5 in Python |
| Defiance index | \|z_access + z_mortality\| ranking |
| Context check | Absolute differences (< 0.5pp despite high z) |

**Visualizations (3):**
1. Quadrant scatter — z_access (x) vs z_mortality (y), labeled countries, ±1 lines
2. Radar chart — Russia, Turkey, global mean across 5 metrics
3. Ranked bar chart — defiance index for all 20 countries

**Narrative:** No true outliers; Russia/Turkey deviate most but absolute differences are noise-level.

---

### Q4: Sensitivity Analysis (`q4_sensitivity_tiers.ipynb`)
**Source:** `v_sensitivity_tiers` (all 9 rows)

| Analysis | Method |
|----------|--------|
| Tier spread | Max-min mortality within each scheme |
| Cross-scheme ANOVA | Eta-squared per scheme |
| Sensitivity matrix | Outcome × scheme ranking comparison |

**Visualizations (3):**
1. 3-panel grouped bar chart — one panel per scheme, bars per tier, same y-axis
2. Tornado chart — range of outcomes per scheme (horizontal bars)
3. Eta-squared heatmap — 3 schemes × 3 outcomes

**Narrative:** Conclusions insensitive to definitions — max spread < 0.04pp across all schemes.

---

### Q5: Sparse Reporting & Uncertainty (`q5_sparse_reporting.ipynb`)
**Source:** `v_sparse_reporting`

| Analysis | Method |
|----------|--------|
| Adequacy summary | 640/640 = adequate |
| CI analysis | Distribution of ci_half_width_mortality |
| Power analysis | `scipy.stats` — minimum N for 1pp detectable difference |
| **Simulated sparsity** | Subsample 5% of data, recompute CIs → show what sparse WOULD look like |

**Visualizations (3):**
1. Forest plot — mortality CI by country, sorted
2. Sample size vs CI width scatter — log(n) vs ci_half_width
3. **Side-by-side forest plots** — full data CIs (left) vs simulated 5% subsample (right)

**Competitive advantage:** Simulating sparsity shows analytical maturity beyond what the data requires.

---

### Q6: Premature Conclusions (`q6_premature_conclusions.ipynb`)
**Source:** `v_premature_conclusions`, synthesis from Q1-Q5

| Analysis | Method |
|----------|--------|
| Confounder check | All 24 combos = no_strong_confounder |
| 5 premature conclusions | Structured framework with evidence |
| Meta-insight | Data is synthetic — expected vs observed correlations |
| Information entropy | Shannon entropy of key columns → quantify uniformity |

**5 Premature Conclusions Framework:**
1. "Rural areas have worse outcomes" — d < 0.01
2. "Healthcare access improves outcomes" — r ≈ 0
3. "Country X is an outlier" — between-country variance is noise
4. "Viral diseases are biggest burden" — artifact of 10/20 diseases being viral
5. "Data supports resource reallocation" — no signal for where to reallocate

**Visualizations (3):**
1. Full correlation matrix heatmap — near-zero off-diagonal = synthetic signature
2. Expected vs observed paired bars — 5 relationships, literature vs actual
3. Evidence quality scorecard — traffic-light heatmap for all 6 questions

**Competitive advantage:** Transparently identifying synthetic data and building a premature-conclusions framework is stronger than forcing false insights.

---

### Executive Summary (`summary_executive.ipynb`)
**Source:** All 6 views

- Summary table: Question | Finding | Confidence | Viz Reference
- 2×3 dashboard grid of best figure from each Q
- Impact-confidence scatter for all 6 questions
- Export all figures at 16:9 presentation resolution
- Formatted assumption log for appendix

---

## Statistical Methods

| Method | Why (not just p-values) |
|--------|------------------------|
| Cohen's d | N=1M makes everything "significant" — effect size matters |
| Eta-squared | Variance explained > significance |
| R-squared | Shows near-zero explanatory power |
| Shannon entropy | Quantifies distribution uniformity |
| Power analysis | Shows N is vastly overpowered |
| Simulated subsampling | Demonstrates uncertainty concepts |

---

## `run.sh` Updates

Add after pipeline step:

```bash
# ── Step 4: Run analysis notebooks ──
mkdir -p reports/figures
for nb in q1_outcome_geography q2_access_vs_outcomes q3_outlier_communities \
          q4_sensitivity_tiers q5_sparse_reporting q6_premature_conclusions \
          summary_executive; do
    echo "[NOTEBOOK] Running $nb..."
    .venv/bin/jupyter nbconvert --execute "notebooks/${nb}.ipynb" \
        --to html --output-dir=reports/ \
        --ExecutePreprocessor.timeout=300 2>&1
done
```

Add `nbconvert` to `requirements.txt`. Add `reports/figures/` to `.gitignore`.

---

## `CLAUDE.md` Updates

Update pipeline order diagram to include Phase 5 (notebooks). Update project structure listing.

---

## Implementation Order

1. Create `notebooks/_helpers.py`
2. Create Q1 through Q6 notebooks (in order)
3. Create `summary_executive.ipynb`
4. Update `run.sh` with notebook execution step
5. Update `requirements.txt` (add `nbconvert`)
6. Update `CLAUDE.md` pipeline diagram
7. Update `.gitignore` (add `reports/figures/`)
8. Run `bash run.sh` end-to-end to verify

---

## Verification

```bash
# All notebooks executed without error
ls reports/q*.html reports/summary_executive.html

# Figures generated
ls reports/figures/*.png | wc -l   # expect ~20+ figures

# Full pipeline + notebooks via run.sh
bash run.sh  # exits 0, all phases pass
```
