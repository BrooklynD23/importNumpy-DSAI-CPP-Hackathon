# Presentation Outline (10–12 slides) — “5 Conclusions That Would Kill Your Policy”

Audience: Datathon judges (non-technical + technical).  
Goal: Show analytical integrity + technical rigor + actionable next steps *without overclaiming*.

**Golden rule:** Every claim is labeled **Descriptive**, **Robustness**, or **Illustrative** (see `docs/prompt_to_data_contract.md`).

---

## Slide 1 — Title + Stakes
- Thesis: “Wrong conclusions cost lives. Here are 5 this dataset tempts you to make — and why they’re premature.”
- One line on dual-track approach: **Observed** vs **Benchmark** (Illustrative).

## Slide 2 — What’s in the data (and what’s not)
- Show: 1M rows; key columns; *missing distance/utilization*.
- Reference: `docs/prompt_to_data_contract.md`.

## Slide 3 — Data quality ≠ data realism
- Claim (Descriptive): dataset is clean (0% missingness/out-of-range).
- Pivot: clean data can still be structurally unrealistic.
- Show: `reports/data_quality_report.md` (1 screenshot or 1 table).

## Slide 4 — Synthetic signatures (headline metrics)
- Claim (Descriptive): near-zero correlations + near-cartesian coverage + label entropy.
- Show: `reports/figures/q6_correlation_matrix.png` and/or a small table from `reports/synthetic_signatures.json`.
- Close: “External validity is limited; we will not force causal policy claims.”

## Slide 5 — Trap #1: “Rural areas have worse outcomes”
- Claim (Descriptive): tier differences are absent.
- Show: `reports/figures/q1_effect_size_dotplot.png` (effect sizes, not p-values).

## Slide 6 — Trap #2: “Access improves outcomes”
- Claim (Descriptive): access↔mortality is flat (R² ~ 0).
- Show: `reports/figures/q2_scatter_access_mortality.png` or `q2_decile_step_chart.png`.
- Add 1 sentence: “Distance-to-care is unmeasured; we use access proxies only.”

## Slide 7 — Trap #3: “Country X is an outlier”
- Claim (Descriptive): highest z-scores exist, but absolute differences are noise-level.
- Show: `reports/figures/q3_quadrant_scatter.png`.

## Slide 8 — Trap #4: “Tier definitions change conclusions”
- Claim (Robustness): conclusions unchanged across 3 schemes.
- Show: `reports/figures/q4_3panel_tier_schemes.png`.

## Slide 9 — Trap #5: “Sparse reporting drives uncertainty here”
- Claim (Descriptive): sparse reporting is not observed here (all groups adequate).
- Show: `reports/figures/q5_forest_plot_full.png`.
- Then (Illustrative): show what sparsity would look like via subsample.
- Show: `reports/figures/q5_forest_full_vs_sparse.png`.

## Slide 10 — Robustness check: repeated-cell sampling
- Claim (Robustness): base vs deduped-cell views agree (no repeated-sampling artifact).
- Show: a compact table from `robustness_delta_summary` (from `reports/summary_executive.html` after updates).

## Slide 11 — Expected vs observed (benchmark split-screen)
- Claim (Illustrative): realistic literature patterns vs observed null patterns.
- Show: `reports/figures/bench_q6_dumbbell_correlations.png`.
- Phrase: “This is why policy prescriptions from this dataset would be premature.”

## Slide 12 — Guardrails + 30/60/90 day plan
- Guardrails (Descriptive policy): minimum data requirements before action.
- Show: `reports/figures/bench_data_readiness_scorecard.png` + `bench_action_timeline.png`.
- Closing: “We know what we’d do with the right data; first we validate/collect it.”

---

## Appendix (Q&A “defense lines”)
- “Where is distance-to-care?” → Not measured; see `docs/prompt_to_data_contract.md` + `reports/prompt_gap_matrix.md`.
- “Isn’t this synthetic?” → Yes; measured signatures; see `reports/synthetic_signatures.json` + `docs/dataset_audit_finding_overview.md`.
- “Why not p-values?” → N=1M makes everything significant; we report effect sizes.

