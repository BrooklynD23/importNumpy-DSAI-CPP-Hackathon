# DND Spring 2026 Datathon — Stakeholder Guide

**Team importNumpy** | Global Health Statistics Analysis

---

## What We Did and Why It Matters

We were given a dataset of 1 million health records spanning 20 countries. The goal was to answer 6 questions about global health patterns — things like "do rural communities have worse health outcomes?" and "does better healthcare access reduce mortality?"

After rigorous analysis, we found something unexpected: **the data doesn't behave like real health data at all.** The numbers look plausible on the surface, but the relationships between variables that always appear in real-world health data are completely absent.

Rather than pretending to find answers that don't exist — or worse, manufacturing misleading policy recommendations — we took a different approach:

1. **Track 1 — Honest:** Show exactly what the data contains (and doesn't)
2. **Track 2 — Benchmark:** Show what real data *would* reveal, and what actions *should* follow

This document explains how we built the analysis and what every chart means in plain language.

---

## Part 1: How the Pipeline Works

Think of our pipeline like an assembly line with 4 stages and a final reporting step.

```
Raw CSV File (1 million rows)
      │
      ▼
 Stage 1: Load & Check
      │  Read the spreadsheet into a database
      │  Verify 1M rows, 25 columns, 3 geography categories
      ▼
 Stage 2: Quality Audit
      │  Flag any invalid values (negative rates, impossible numbers)
      │  Write a quality report so we know what we're working with
      ▼
 Stage 3: Clean & Categorise
      │  Apply corrected disease categories (the original labels had errors)
      │  Create 3 versions of "urban vs rural" (for sensitivity testing)
      │  Remove any flagged bad rows
      ▼
 Stage 4: Build 6 Answer Tables
      │  One summary table per competition question
      │  Each table pre-aggregates the data for fast analysis
      ▼
 Stage 5: Run 8 Analysis Notebooks
         ├── Q1: Do rural areas have worse outcomes?
         ├── Q2: Does healthcare access improve survival?
         ├── Q3: Are any countries unusually good or bad?
         ├── Q4: Does our rural/urban definition change results?
         ├── Q5: How reliable is the data in data-sparse regions?
         ├── Q6: Which common conclusions would be premature?
         ├── Benchmark: What would real data look like?
         └── Summary: Full synthesis + figures
```

Everything runs automatically from a single command (`bash run.sh`). A non-technical person can double-click the script and get all 30 charts and 8 HTML reports with no manual steps.

### Why DuckDB?

We store and query everything in DuckDB — a high-performance analytical database that runs entirely on your laptop. No servers, no cloud, no accounts needed. With 1 million rows, Excel would crash; DuckDB handles it in seconds.

---

## Part 2: The Core Finding — A Tale of Two Datasets

Before diving into individual charts, here is the most important thing to understand:

> **This dataset was synthetically generated.** The numbers were created by a computer algorithm, not collected from real hospitals or registries. That algorithm assigned each row's values independently — meaning healthcare access in a country has no connection to that country's mortality rate, income level, or anything else.

In the real world, these things are tightly connected. Wealthier countries have better healthcare access. Better healthcare access means lower mortality. Communities with higher education have lower disease rates. These patterns are so consistent across decades of global health research that their *absence* is itself a strong signal.

Our "Dual-Track" approach uses this absence as a teaching moment:
- The red bars/dots in our charts always show **what this dataset says**
- The blue bars/dots always show **what real data would say**
- The gap between them is the evidence gap

---

## Part 3: Figure-by-Figure Guide

### The Dashboard Overview

**`summary_dashboard_grid.png`**

A six-panel summary showing the headline result for each question. All six panels tell the same story from different angles: the data is statistically flat. The bars are the same height, the scatter plots are clouds with no direction, and the forest plot shows every country with identical confidence intervals. For a practitioner, seeing six null results in a row is itself informative — real datasets never look like this.

---

### Q1: Do Rural Areas Have Worse Health Outcomes?

**`q1_bar_mortality_by_tier.png`** — *The three-bar chart*

Each bar shows average mortality for Rural (green), Peri-urban (orange), and Urban (red) areas. The error bars (the small T-shapes at the top) show the uncertainty range. **All three bars are the same height: ~5.05%.** The error bars don't even overlap with different values — they're microscopically small because we have so many data points.

In plain terms: the data says rural and urban areas have *exactly the same* mortality rate. In the real world, rural areas in lower-income countries typically have 50–150% higher mortality than urban areas.

---

**`bench_q1_tier_comparison.png`** — *The side-by-side comparison*

This is the "what vs what should be" chart for Q1. The **red bars** (left of each pair) show the flat ~5% we observed. The **blue bars** (right of each pair) show what WHO data tells us about rural-urban gaps.

- Rural benchmark: **12.5%** — more than twice the observed value
- Urban benchmark: **5.0%** — matches observed (only group that does)
- Expected gap: **~7.5 percentage points**
- Observed gap: **<0.01 percentage points** (essentially zero)

**What this means for policy:** If this were real data, you would see a clear rural crisis and direct resources accordingly. Because the gap is absent, any rural-targeted intervention funded by this data alone would be based on a false premise.

---

### Q2: Does Healthcare Access Improve Survival?

**`q2_scatter_access_mortality.png`** — *The dot cloud*

Each dot represents a group of patients. The horizontal position shows how much healthcare access they had; the vertical position shows their mortality rate. **In real health data, this cloud should slope downward** — more access, lower mortality. Here the cloud is a perfect rectangle. Knowing a community's healthcare access level tells you absolutely nothing about its mortality rate.

---

**`bench_q2_scatter_comparison.png`** — *The side-by-side scatter*

Two versions of the same chart placed side by side on identical axes so you can compare directly.

- **Left (blue) — Benchmark:** A clear downward slope. The red regression line drops sharply. Communities with 20% access have ~13% mortality; those with 90% access have ~5%. This is what 40 years of global health research consistently finds (r = –0.67).
- **Right (red) — Observed:** A horizontal smear. The regression line is nearly flat (r = –0.02). Healthcare access and mortality are completely unrelated in this dataset.

**What this means for policy:** A decision to build more clinics in low-access areas based on this data would have no statistical backing. The correlation that should justify the investment simply doesn't exist here.

---

### Q3: Are Any Countries Unusually Good or Bad?

**`bench_q3_country_spread.png`** — *The double horizontal bar chart*

This shows all 20 countries sorted by mortality rate.

- **Left panel (blue) — Benchmark:** A wide spread from ~3% to ~14%. Two green bars at the bottom are "outlier" countries — places like Cuba, which have low incomes but surprisingly low mortality due to strong public health systems. These are the anomalies worth studying.
- **Right panel (red) — Observed:** All 20 countries bunched between 5.02% and 5.10%. On the 0–20% scale used by the benchmark panel, you can barely see the variation. Russia and Turkey appear at the top, South Africa at the bottom — but the absolute difference between them is less than a tenth of a percentage point.

**What this means for policy:** In real health data, identifying outlier countries ("how does Rwanda outperform its income peers on maternal mortality?") generates actionable lessons. Here, there are no outliers to learn from.

---

### Q4: Does Our Urban/Rural Definition Change the Answers?

**`bench_q4_sensitivity_comparison.png`** — *The grouped bar chart on tier definitions*

We tested three different ways of defining "rural" vs "urban":
- **3-Tier** (our default): Rural / Peri-urban / Urban
- **Binary**: Simply Rural / Urban
- **4-Tier**: Rural / Peri-urban / Semi-urban / Urban

In real data, how you draw these boundaries matters a lot — the binary split in particular can mask nuance by lumping "peri-urban" communities with fully urban ones.

- **Blue bars (benchmark):** Each tier scheme produces a different mortality spread — 5.2pp, 9.1pp, and 7.5pp respectively. The binary scheme masks 2.3pp of heterogeneity that the 4-tier scheme reveals.
- **Red bars (observed):** All three spreads are essentially zero (0.001pp, 0.014pp, 0.014pp). The observed red bars are invisible at the bottom of each pair.

**What this means for policy:** In real data, this analysis is important for picking the right classification scheme before drawing policy conclusions. Here it's moot because there's nothing to be sensitive to.

---

### Q5: How Reliable Is the Data in Data-Sparse Regions?

**`bench_q5_forest_comparison.png`** — *The double forest plot*

A forest plot shows each country as a dot with a horizontal line through it. The dot is the average; the line shows the uncertainty range (confidence interval). A short line means we're confident in that estimate. A long line means we're uncertain.

- **Left (blue) — Benchmark:** Countries have very different line lengths. Poorer countries (lower access) have longer lines — meaning their estimates are less reliable because we'd have fewer data points from them. Four countries shown in grey have insufficient data and should not be included in policy decisions.
- **Right (red) — Observed:** Every country has an identical tiny dot with almost invisible lines. This is because all 20 countries have over 50,000 observations each. We are extremely precise — but extremely precise at measuring the same meaningless number (~5.05%) for every country.

**What this means for policy:** Real-world health decisions require acknowledging which regions we know less about. This dataset, paradoxically, gives us too much data — so much that the statistical uncertainty becomes negligible, hiding the practical problem that all countries appear identical.

---

### Q6: Which Common Conclusions Would Be Premature?

**`bench_q6_dumbbell_correlations.png`** — *The dumbbell chart*

This is arguably the most important chart in the entire analysis. Each row is a relationship that global health research has established over decades. The **blue dot** shows what that relationship looks like in the literature. The **red dot** shows what this dataset produces. The line connecting them is the "evidence gap."

Reading the chart row by row:

| Relationship | Expected (Blue) | Observed (Red) | What it means |
|---|---|---|---|
| Access → Mortality | –0.45 (strong negative) | ~0 | More access *should* reduce deaths; here it doesn't |
| Income → Access | +0.60 (strong positive) | ~0 | Richer countries *should* have better access; here they don't |
| Education → Mortality | –0.40 (moderate negative) | ~0 | More educated populations *should* be healthier; here they aren't |
| Urban → Access | +0.50 (moderate positive) | ~0 | Urban areas *should* have better access; here they don't |
| Doctors → Recovery | +0.35 (moderate positive) | ~0 | More doctors *should* mean faster recovery; here they don't |
| Income → Mortality | –0.50 (strong negative) | ~0 | Wealthier countries *should* have lower mortality; here they don't |
| Prevalence → DALYs | +0.65 (strong positive) | ~0 | More disease *should* mean more years lost; here they're unrelated |
| Beds → Recovery | +0.30 (moderate positive) | ~0 | More hospital beds *should* mean better recovery; here they don't |

Every single red dot sits at zero. Every single blue dot is far away. This pattern — eight foundational relationships all broken simultaneously — is the statistical fingerprint of synthetically generated data.

**What this means for policy:** Any recommendation built on this data — "invest in doctors," "expand hospital beds," "target low-income regions" — would have zero statistical support. The 8 gaps shown here are not small discrepancies; they are the entire signal that would justify action.

---

### The Data Readiness Scorecard

**`bench_data_readiness_scorecard.png`** — *The traffic-light grid*

This is a simple yes/no/partial assessment of what this dataset has versus what is needed before any policy action.

- **Red (Absent / Critical):** Five criteria are completely missing: geographic variation between areas, access-outcome relationships, differences between countries, realistic data gaps in poorer regions, and confounding structure (how income/education interact with health). All five are rated **Critical** — these are not nice-to-haves, they are the foundation of any evidence-based health policy.
- **Yellow (Partial / Moderate or High):** Temporal trends, demographic breakdown, and disease-specific profiles are partially present. They're not enough on their own.
- **Green (Present):** None in the dataset's column.

**The bottom line:** This dataset fails 5 of 8 critical policy prerequisites. It is not a foundation for resource allocation decisions.

---

### The 30/60/90-Day Action Plan

**`bench_action_timeline.png`** — *The Gantt chart*

This chart answers the question: *"If the benchmark findings were real, what would you actually do about it?"*

Each row (Q1 through Q6) is a competition question. Each coloured bar is a specific action. Colours indicate urgency:
- **Red (Critical):** Deploy mobile health units to rural districts; fund rural infrastructure — things that directly save lives
- **Orange (High):** Pilot telemedicine, build predictive models, fill data gaps — important medium-term work
- **Blue (Medium):** Standardise definitions, publish quality bulletins — important for long-term data infrastructure

This demonstrates that our team understands not just how to analyse data, but what to *do* with analysis. Even though these actions are hypothetical for this synthetic dataset, the logic chain from finding → action is explicit and grounded.

---

## Part 4: The Honest Conclusion

We believe that being wrong with confidence is more dangerous than being uncertain with honesty.

Teams that forced positive findings from this dataset would produce:
- Incorrect rural health interventions (the rural crisis doesn't exist here)
- Misallocated healthcare access spending (no correlation to act on)
- False identification of "outlier" countries worth studying (they're statistically identical)

Our contribution is demonstrating that **analytical integrity is itself a skill** — knowing when NOT to make a recommendation is as important as knowing when to act.

At the same time, by showing what the data *should* look like and what actions *would* follow, we demonstrate full policy-readiness for when better data arrives.

---

## Quick Reference: All 30 Figures

| Figure | Question | What it shows |
|--------|----------|---------------|
| `q1_bar_mortality_by_tier` | Q1 | Mortality rates by rural/urban tier |
| `q1_heatmap_country_tier` | Q1 | Country × tier mortality grid |
| `q1_violin_mortality` | Q1 | Distribution shape of mortality across tiers |
| `q1_effect_size_dotplot` | Q1 | Cohen's d values (statistical effect sizes) |
| `q2_scatter_access_mortality` | Q2 | Access vs mortality scatter |
| `q2_faceted_scatter_by_tier` | Q2 | Access vs mortality, split by tier |
| `q2_decile_step_chart` | Q2 | Mortality by access decile |
| `q2_correlation_histogram` | Q2 | Distribution of group-level correlations |
| `q3_quadrant_scatter` | Q3 | Countries on access/mortality axes |
| `q3_defiance_index_ranking` | Q3 | Countries ranked by "outlier score" |
| `q3_radar_deviators` | Q3 | Multi-dimensional profile of top deviators |
| `q4_3panel_tier_schemes` | Q4 | Mortality under all 3 tier schemes |
| `q4_eta_squared_heatmap` | Q4 | Variance explained by tier (per disease) |
| `q4_tornado_range` | Q4 | Sensitivity range for each tier scheme |
| `q5_forest_plot_full` | Q5 | Full forest plot for all countries |
| `q5_forest_full_vs_sparse` | Q5 | Full vs simulated-sparse data comparison |
| `q5_n_vs_ci_width` | Q5 | Uncertainty as a function of sample size |
| `q6_correlation_matrix` | Q6 | Full correlation heatmap of all variables |
| `q6_expected_vs_observed` | Q6 | Three key expected vs observed correlations |
| `q6_evidence_scorecard` | Q6 | Traffic-light scorecard of relationships |
| `summary_dashboard_grid` | All | Best figure from each question in one view |
| `summary_impact_confidence` | All | Each question scored on impact vs confidence |
| `bench_q1_tier_comparison` | Benchmark | Tier mortality: observed vs WHO benchmark |
| `bench_q2_scatter_comparison` | Benchmark | Scatter side-by-side: realistic vs flat |
| `bench_q3_country_spread` | Benchmark | Country spread: 13pp benchmark vs <0.5pp observed |
| `bench_q4_sensitivity_comparison` | Benchmark | Sensitivity spreads: benchmark vs observed |
| `bench_q5_forest_comparison` | Benchmark | Forest plot: varying uncertainty vs uniform |
| `bench_q6_dumbbell_correlations` | Benchmark | 8-pair evidence gap dumbbell chart |
| `bench_data_readiness_scorecard` | Benchmark | Traffic-light data readiness assessment |
| `bench_action_timeline` | Benchmark | 30/60/90-day action Gantt chart |
