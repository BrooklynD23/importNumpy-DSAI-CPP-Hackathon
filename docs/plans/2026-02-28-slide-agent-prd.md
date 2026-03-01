# PRD: PowerPoint Slide Agent — DND Spring 2026 Datathon

**Date:** 2026-02-28
**Team:** importNumpy
**Output:** `presentation/DND_2026_importNumpy.pptx`
**Tool:** python-pptx
**Figures source:** `reports/figures/` (all 30 PNGs confirmed generated)

---

## 1. Goal

Build a complete 12-slide PowerPoint presentation (`presentation/DND_2026_importNumpy.pptx`) using python-pptx. The presentation follows the "5 Conclusions That Would Kill Your Policy" narrative framed in `docs/plans/2026-02-24-presentation-framing-design.md`. All figures are pre-generated at 300 DPI in `reports/figures/`. The agent must create `presentation/build_slides.py` and run it.

---

## 2. Prerequisites

### 2a. Add python-pptx to requirements.txt
Append the following line to `requirements.txt`:
```
python-pptx>=1.0.0
```
Then install:
```bash
.venv/bin/pip install python-pptx>=1.0.0
```

### 2b. Verify figure paths exist before running
All figures referenced in this PRD are in `reports/figures/`. The script must assert each path exists before building slides and print a warning for any missing file (do not crash — skip the image and add a placeholder text box instead).

---

## 3. Design System

```python
# All measurements in Inches() unless stated otherwise
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)

# Colors (RGBColor)
NAVY       = RGBColor(0x1B, 0x3A, 0x6B)   # Primary — titles, headers
CORAL      = RGBColor(0xE8, 0x5D, 0x40)   # Accent — Trap slides header bar
GREEN      = RGBColor(0x2D, 0x8C, 0x4E)   # Safer frame / Descriptive badge
BLUE_LABEL = RGBColor(0x1B, 0x6B, 0xB0)   # Robustness badge
PURPLE     = RGBColor(0x7B, 0x5E, 0xA7)   # Illustrative badge
LIGHT_GRAY = RGBColor(0xF2, 0xF4, 0xF8)   # Slide background
MID_GRAY   = RGBColor(0x9E, 0x9E, 0x9E)   # Footer / captions
DARK_GRAY  = RGBColor(0x2D, 0x2D, 0x2D)   # Body text
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)

# Typography
FONT_FAMILY    = "Calibri"
SIZE_TITLE     = Pt(30)
SIZE_SUBTITLE  = Pt(18)
SIZE_BODY      = Pt(15)
SIZE_CAPTION   = Pt(11)
SIZE_BADGE     = Pt(10)
SIZE_FOOTER    = Pt(9)

# Layout constants
MARGIN_L  = Inches(0.45)
MARGIN_R  = Inches(0.45)
TITLE_BAR_H   = Inches(1.15)
CONTENT_TOP   = Inches(1.25)
CONTENT_H     = Inches(5.75)
COL_MID       = Inches(6.67)   # center divider for 2-col layouts
COL_W         = Inches(5.95)   # each column width in 2-col layout
COL_GAP       = Inches(0.30)
FOOTER_TOP    = Inches(7.05)
FOOTER_H      = Inches(0.35)
```

### 3a. Helper functions to implement

```python
def add_rect(slide, left, top, width, height, fill_rgb, line=False):
    """Add a filled rectangle shape."""

def add_text_box(slide, text, left, top, width, height,
                 font_size, bold=False, color=DARK_GRAY,
                 align=PP_ALIGN.LEFT, wrap=True):
    """Add a text box with consistent formatting."""

def add_image(slide, img_path, left, top, width, height):
    """Add an image; if path missing, add gray placeholder with filename."""

def add_evidence_badge(slide, label, left, top):
    """
    Add a small colored pill badge.
    label in {"DESCRIPTIVE", "ROBUSTNESS", "ILLUSTRATIVE"}
    Colors: DESCRIPTIVE=GREEN, ROBUSTNESS=BLUE_LABEL, ILLUSTRATIVE=PURPLE
    Size: width=Inches(1.6), height=Inches(0.28)
    """

def add_footer(slide, slide_num, total=12):
    """Add bottom footer: team name left, slide number right."""

def add_title_bar(slide, title_text, bar_color=NAVY, text_color=WHITE):
    """Full-width colored bar across top with white title text."""

def add_trap_header(slide, trap_num):
    """
    Coral bar with 'TRAP #N' label, height=Inches(0.45), width=full slide.
    Sits above the main title bar or replaces it for trap slides.
    """
```

---

## 4. Slide Specifications

### Slide 1 — Title

**Layout:** Blank

**Elements:**
1. Full-width navy rectangle: `left=0, top=0, width=SLIDE_W, height=Inches(3.8)`, fill=NAVY
2. Title text box (white): `"5 Conclusions That Would Kill Your Policy"`, left=MARGIN_L, top=Inches(0.6), width=Inches(12.4), height=Inches(1.6), SIZE_TITLE×1.3=Pt(38), bold=True, color=WHITE
3. Subtitle text box (white, lighter): `"A Data Integrity Analysis of Global Health Statistics"`, top=Inches(2.1), SIZE_SUBTITLE, color=WHITE, bold=False
4. Team text box (navy): `"Team importNumpy"`, top=Inches(4.2), SIZE_BODY, bold=True, color=NAVY
5. Event text box: `"DND Spring 2026 Datathon  ·  Cal Poly Pomona"`, top=Inches(4.7), SIZE_CAPTION, color=MID_GRAY
6. Data note: `"Dataset: Global Health Statistics  ·  1,000,000 rows  ·  20 countries  ·  2000–2024"`, top=Inches(5.2), SIZE_CAPTION, color=MID_GRAY
7. Footer: slide 1 of 12

---

### Slide 2 — What's in the Data (and What's Not)

**Title bar:** "What's in the Data — and What's Not"

**Layout:** 2-column

**Left column header (green bar):** "MEASURED ✓" (white text, SIZE_BADGE bold)
**Left column content (SIZE_BODY bullets):**
```
• Outcomes: mortality_rate, recovery_rate, DALYs
• Access proxies: healthcare_access, doctors_per_1000,
  hospital_beds_per_1000, resource_index
• Socioeconomic: per_capita_income, education_index
• Geography proxy: urbanization_rate → 3 tier schemes
• Structure: country, year, disease, age_group, gender
• Scale: 1M rows · 119,978 unique combinations
```

**Right column header (coral bar):** "NOT MEASURED ✗" (white text, SIZE_BADGE bold)
**Right column content (SIZE_BODY bullets, CORAL text):**
```
• Distance-to-care (travel time, proximity)
• Facility locations or density maps
• Utilization (visits, admissions, claims)
• Continuity-of-care metrics
• Real-world reporting variation or missingness
```

**Bottom note (italic, SIZE_CAPTION, NAVY):**
`"All claims are labeled: DESCRIPTIVE | ROBUSTNESS | ILLUSTRATIVE — see appendix for evidence contract."`

**Badge:** DESCRIPTIVE (bottom right)
**Footer:** slide 2 of 12

---

### Slide 3 — Clean Data ≠ Realistic Data

**Title bar:** "Clean Data ≠ Realistic Data — Six Synthetic Signatures"

**Layout:** 2-column

**Left column header (green bar):** "DATA QUALITY ✓"
**Left column bullets:**
```
• 0% missingness across all 25 columns
• 0 out-of-range values on all rate columns
• 1,000,000 rows, all pass quality flags
• 119,978 / 120,000 possible combinations present (99.98%)
• All 20 disease names correctly mapped
```

**Right column header (coral bar):** "SYNTHETIC SIGNATURES ⚠"
**Right column bullets (DARK_GRAY, each line preceded by emoji):**
```
⚠  Near-Cartesian coverage: 99.98% of all (country × year
   × disease × age × gender) cells filled
⚠  Near-zero dependence: |r|max = 0.0023 across 14 variables
⚠  Bounded-range match: observed mean/SD match Uniform(a,b)
   expectations to <0.01% error on all rate columns
⚠  Homogeneous countries: mortality SD across 20 countries = 0.013
   (ANOVA η² = 0.0000208)
⚠  Randomized disease labels: entropy = 3.459 ≈ theoretical max
⚠  Strict 2-decimal quantization: 100% of numeric values
```

**Badge:** DESCRIPTIVE
**Footer:** slide 3 of 12

---

### Slide 4 — Synthetic Signatures: Headline Metrics

**Title bar:** `'Geography Explains 0.002% of Mortality Variance'`

**Layout:** Left table + right image

**Left side** (left=MARGIN_L, top=CONTENT_TOP, width=COL_W):

Table (3 columns × 5 rows) with header row fill=NAVY, text=WHITE:

| Metric | This Dataset | Real-World Expected |
|--------|-------------|---------------------|
| Access ↔ Mortality (r) | 0.00008 | −0.30 to −0.50 |
| Income ↔ Mortality (r) | −0.0015 | −0.20 to −0.40 |
| Country ANOVA η² | 0.0000208 | 0.05 to 0.30 |
| Year trend η² | 0.0000106 | 0.01 to 0.15 |

Below table (SIZE_CAPTION, italic, MID_GRAY):
`"Expected ranges from WHO/Lancet global health literature. Observed values are descriptive of this dataset only."`

**Right side** image: `reports/figures/bench_q6_dumbbell_correlations.png`
Position: left=COL_MID+COL_GAP, top=CONTENT_TOP, width=COL_W, height=Inches(5.2)

**Badge:** DESCRIPTIVE + ILLUSTRATIVE (both)
**Footer:** slide 4 of 12

---

### Slide 5 — Trap #1: Rural Outcomes

**Trap header bar** (coral, height=Inches(0.42)): `"TRAP #1"`

**Title bar** (navy, below trap bar): `'"Rural Areas Have Worse Outcomes" — Evidence: ABSENT'`

**Layout:** Left bullets + right image

**Left bullets (SIZE_BODY):**
```
Common claim:
  Urban/rural classification predicts health outcomes.

What we found (DESCRIPTIVE):
  • Cohen's d < 0.01 for all tier pairs (negligible effect)
  • ANOVA η² = 0.0000208 (geography explains 0.002%)
  • p < 0.001 — but N=1M makes everything significant
  • Absolute mortality difference Rural vs Urban: < 0.05pp

Why it's premature:
  Statistical significance ≠ practical significance.
  With 1M rows, any noise clears p-value thresholds.

Safer framing:
  "We cannot distinguish outcomes across urbanization
  tiers with this dataset. Report effect sizes, not p-values."
```

**Right image:** `reports/figures/q1_effect_size_dotplot.png`
Position: left=COL_MID+COL_GAP, top=CONTENT_TOP, width=COL_W, height=Inches(5.0)

**Green text box (bottom left, SIZE_CAPTION):**
`"✓ Use effect sizes (Cohen's d, η²), not p-values with large N"`

**Badge:** DESCRIPTIVE
**Footer:** slide 5 of 12

---

### Slide 6 — Trap #2: Access → Outcomes

**Trap header bar** (coral): `"TRAP #2"`

**Title bar:** `'"Healthcare Access Improves Outcomes" — Evidence: FLAT'`

**Layout:** Left bullets + right image

**Left bullets:**
```
Common claim:
  Higher healthcare access scores → lower mortality rates.

What we found (DESCRIPTIVE):
  • Pearson r (access ↔ mortality) = 0.00008
  • R² < 0.000001 — access explains essentially 0% of variance
  • No dose-response at any access decile threshold
  • Spearman ρ consistent: no monotonic relationship

Critical gap:
  Distance-to-care and utilization are NOT in this dataset.
  "Healthcare access" is a proxy index, not a distance measure.

Safer framing:
  "This dataset cannot support an access-outcome causal claim.
  Collecting travel time and utilization data is the prerequisite."
```

**Right image:** `reports/figures/q2_scatter_access_mortality.png`
Position: right column, full height

**Red text box (bottom, SIZE_CAPTION, CORAL):**
`"⚠ Distance-to-care: NOT MEASURED. Access proxies used only. See prompt_gap_matrix.md."`

**Badge:** DESCRIPTIVE
**Footer:** slide 6 of 12

---

### Slide 7 — Trap #3: Country Outliers

**Trap header bar** (coral): `"TRAP #3"`

**Title bar:** `'"Country X Is an Outlier Worth Studying" — Evidence: NOISE'`

**Layout:** Left bullets + right image

**Left bullets:**
```
Common claim:
  High z-score countries represent exceptional systems
  worth studying or emulating.

What we found (DESCRIPTIVE):
  • Some countries show high z-scores on access vs outcomes
  • Absolute mortality differences: < 0.5 percentage points
  • Between-country SD: 0.013 on mortality (scale: 0–10)
  • Effect is noise-level at this resolution

Why it's premature:
  Z-scores inflate when within-group variance is near-zero.
  A 0.5pp absolute difference is not a policy signal.

Safer framing:
  "No country deviates meaningfully in absolute terms.
  Statistical outliers here are artifacts of near-zero variance,
  not evidence of a distinctive health system."
```

**Right image:** `reports/figures/q3_quadrant_scatter.png`
Position: right column, full height

**Badge:** DESCRIPTIVE
**Footer:** slide 7 of 12

---

### Slide 8 — Trap #4: Tier Definitions

**Trap header bar** (coral): `"TRAP #4"`

**Title bar:** `'"Tier Definitions Change Conclusions" — Evidence: IRRELEVANT'`

**Layout:** Left bullets + right image

**Left bullets:**
```
Common claim:
  How you define "urban" vs "rural" changes your findings.

What we found (ROBUSTNESS):
  • 3 tier schemes tested: Default 3-tier, Binary, 4-tier
  • Maximum spread across schemes: < 0.04 percentage points
  • ANOVA η² ~ 0 under all three definitions
  • Conclusions are identical regardless of classification choice

Why this matters:
  Robustness is confirmed — but only because there is
  no signal to be sensitive to in the first place.
  Tier choice is genuinely irrelevant when the underlying
  effect size is zero.

Safer framing:
  "Our robustness check is valid, but it validates
  a null result — not a policy-relevant pattern."
```

**Right image:** `reports/figures/q4_3panel_tier_schemes.png`
Position: right column, full height

**Badge:** ROBUSTNESS
**Footer:** slide 8 of 12

---

### Slide 9 — Trap #5: Sparse Reporting

**Trap header bar** (coral): `"TRAP #5"`

**Title bar:** `'"Sparse Reporting Drives Uncertainty Here" — Evidence: NOT OBSERVED'`

**Layout:** Left bullets + right image

**Left bullets:**
```
Common claim:
  Data-sparse regions show high uncertainty that distorts
  conclusions about access and outcomes.

What we found (DESCRIPTIVE):
  • Missingness: 0% across all 25 columns
  • All 640 subgroups (country × disease × age × gender):
    count ≥ 30 — all above minimum threshold
  • Confidence intervals are uniformly narrow

Simulation (ILLUSTRATIVE):
  We demonstrate what sparsity would look like via
  subsampling: removing 95% of data widens CIs dramatically.
  This is what the data WOULD show if sparse — it doesn't.

Safer framing:
  "Sparse reporting is a real-world concern we cannot
  assess from this dataset. The dataset is fully populated
  by design. We model the risk via simulation only."
```

**Right image:** `reports/figures/q5_forest_full_vs_sparse.png`
Position: right column, full height

**Badge:** DESCRIPTIVE (top badge) + ILLUSTRATIVE (second badge, offset below first)
**Footer:** slide 9 of 12

---

### Slide 10 — Robustness: Repeated-Cell Check

**Title bar:** "Results Hold Under Repeated-Cell Robustness Check"

**Layout:** Full-width content (no image, table-focused)

**Top intro text (SIZE_BODY):**
`"Each (country × year × disease × age × gender) cell appears ~8.3 times in the dataset. We compared base views vs. dedup-at-cell-grain views to confirm repeated sampling does not inflate any finding."`

**Center table** (5 columns × 7 rows including header), positioned:
left=MARGIN_L, top=Inches(2.2), width=Inches(12.4), height=Inches(3.5)

Header row (fill=NAVY, white text):

| Question | Base Value | Deduped Value | Delta | Conclusion |
|----------|-----------|--------------|-------|------------|
| Q1 Mortality tier gap | 0.0492 pp | 0.0489 pp | 0.0003 pp | No artifact |
| Q2 Access↔mortality r | 0.00008 | 0.00007 | 0.00001 | No artifact |
| Q3 Max country z-score | 2.31 | 2.28 | 0.03 | No artifact |
| Q4 Tier scheme spread | 0.038 pp | 0.037 pp | 0.001 pp | No artifact |
| Q5 Min group count | 8,318 | 1 | — | By design |
| Q6 Max |r| any pair | 0.0023 | 0.0021 | 0.0002 | No artifact |

**Bottom note (SIZE_CAPTION, GREEN):**
`"✓ All deltas are noise-level. Repeated sampling per cell does not create spurious patterns."`

**Badge:** ROBUSTNESS
**Footer:** slide 10 of 12

---

### Slide 11 — Expected vs Observed

**Title bar:** "This Is Why Policy Prescriptions Would Be Premature"

**Layout:** 2-column split-screen

**Left column header (navy bar):** "REAL-WORLD BENCHMARK (Illustrative)"
**Left image:** `reports/figures/bench_q2_scatter_comparison.png`
Position: left=MARGIN_L, top=Inches(1.7), width=COL_W, height=Inches(4.5)

**Left caption (SIZE_CAPTION, MID_GRAY):**
`"Literature-based: access ↔ mortality r ≈ −0.45"`

**Right column header (coral bar):** "THIS DATASET (Descriptive)"
**Right image:** `reports/figures/q2_scatter_access_mortality.png`
Position: right column, top=Inches(1.7), width=COL_W, height=Inches(4.5)

**Right caption (SIZE_CAPTION, CORAL):**
`"Observed: r = 0.00008 — effectively zero"`

**Bottom center text (SIZE_BODY, NAVY, bold, centered):**
`"The gap between benchmark and observed is the reason policy prescriptions from this dataset would be premature."`

**Badge:** ILLUSTRATIVE + DESCRIPTIVE
**Footer:** slide 11 of 12

---

### Slide 12 — Guardrails + Action Plan

**Title bar:** "What Responsible Analysis Requires Before Policy Action"

**Layout:** 2-column

**Left column header (navy bar):** "DATA READINESS SCORECARD"
**Left image:** `reports/figures/bench_data_readiness_scorecard.png`
Position: left=MARGIN_L, top=Inches(1.7), width=COL_W, height=Inches(4.2)

**Left caption (SIZE_CAPTION, MID_GRAY):**
`"Traffic-light assessment: 8 data requirements for responsible policy analysis"`

**Right column header (green bar):** "30 / 60 / 90-DAY ROADMAP"
**Right image:** `reports/figures/bench_action_timeline.png`
Position: right column, top=Inches(1.7), width=COL_W, height=Inches(4.2)

**Right caption (SIZE_CAPTION, MID_GRAY):**
`"12 concrete next steps — deployable on real data when collected"`

**Bottom full-width text box (italic, SIZE_CAPTION, NAVY, centered):**
`'"The most valuable analysis is the one that knows when NOT to make a recommendation — and shows exactly what it WOULD recommend with the right data."'`

**Badge:** ILLUSTRATIVE
**Footer:** slide 12 of 12

---

## 5. Script Structure

Create `presentation/build_slides.py` with the following top-level structure:

```python
#!/usr/bin/env python3
"""
Build DND 2026 Datathon presentation.
Run: .venv/bin/python presentation/build_slides.py
Output: presentation/DND_2026_importNumpy.pptx
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
import sys

# --- Paths ---
ROOT = Path(__file__).parent.parent
FIGURES = ROOT / "reports" / "figures"
OUTPUT  = ROOT / "presentation" / "DND_2026_importNumpy.pptx"

# --- Design constants (see Section 3 above) ---
# ... define all constants here ...

# --- Helpers ---
def add_rect(...): ...
def add_text_box(...): ...
def add_image(...): ...
def add_evidence_badge(...): ...
def add_footer(...): ...
def add_title_bar(...): ...
def add_trap_header(...): ...

# --- Slide builders ---
def build_slide_01(prs): ...  # Title
def build_slide_02(prs): ...  # What's in the data
def build_slide_03(prs): ...  # Clean ≠ Realistic
def build_slide_04(prs): ...  # Synthetic signatures headline
def build_slide_05(prs): ...  # Trap 1
def build_slide_06(prs): ...  # Trap 2
def build_slide_07(prs): ...  # Trap 3
def build_slide_08(prs): ...  # Trap 4
def build_slide_09(prs): ...  # Trap 5
def build_slide_10(prs): ...  # Robustness check
def build_slide_11(prs): ...  # Expected vs Observed
def build_slide_12(prs): ...  # Guardrails + Action Plan

# --- Main ---
def main():
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.50)

    build_slide_01(prs)
    build_slide_02(prs)
    build_slide_03(prs)
    build_slide_04(prs)
    build_slide_05(prs)
    build_slide_06(prs)
    build_slide_07(prs)
    build_slide_08(prs)
    build_slide_09(prs)
    build_slide_10(prs)
    build_slide_11(prs)
    build_slide_12(prs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT}")

if __name__ == "__main__":
    main()
```

---

## 6. Figure → Slide Mapping (Quick Reference)

| Slide | Figure file | Position |
|-------|------------|---------|
| 4 | `bench_q6_dumbbell_correlations.png` | Right column |
| 5 | `q1_effect_size_dotplot.png` | Right column |
| 6 | `q2_scatter_access_mortality.png` | Right column |
| 7 | `q3_quadrant_scatter.png` | Right column |
| 8 | `q4_3panel_tier_schemes.png` | Right column |
| 9 | `q5_forest_full_vs_sparse.png` | Right column |
| 11 (left) | `bench_q2_scatter_comparison.png` | Left column |
| 11 (right) | `q2_scatter_access_mortality.png` | Right column |
| 12 (left) | `bench_data_readiness_scorecard.png` | Left column |
| 12 (right) | `bench_action_timeline.png` | Right column |

---

## 7. Evidence Badge Placement Rules

- Slides 2, 3, 5, 6, 7: badge = **DESCRIPTIVE** (green), bottom-right of content area
- Slide 4: badges = **DESCRIPTIVE** + **ILLUSTRATIVE** (stacked)
- Slides 8, 10: badge = **ROBUSTNESS** (blue)
- Slide 9: badges = **DESCRIPTIVE** + **ILLUSTRATIVE** (stacked)
- Slides 11, 12: badges = **ILLUSTRATIVE** + **DESCRIPTIVE** (stacked)
- Badge position: right=Inches(12.88), top=Inches(6.55), width=Inches(1.65), height=Inches(0.30)
- When stacking 2 badges, second badge top = first + Inches(0.35)

---

## 8. Verification Checklist

After running `presentation/build_slides.py`, verify:

- [ ] `presentation/DND_2026_importNumpy.pptx` exists and is non-zero bytes
- [ ] File opens in PowerPoint/LibreOffice without errors
- [ ] Slide count = 12
- [ ] Slide 1 shows navy header and white title text
- [ ] Slides 5–9 show coral trap header bar
- [ ] All 10 figure images are embedded (no broken image icons)
- [ ] Footer shows correct slide numbers (1 of 12 through 12 of 12)
- [ ] Evidence badges appear on all content slides
- [ ] Slide 10 table has 6 data rows + 1 header row

---

## 9. Run Command

```bash
cd /path/to/importNumpy-DSAI-CPP-Hackathon
.venv/bin/pip install python-pptx>=1.0.0
.venv/bin/python presentation/build_slides.py
```

Output: `presentation/DND_2026_importNumpy.pptx`
