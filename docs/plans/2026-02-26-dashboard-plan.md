# Dashboard Implementation Plan
**Date:** February 26, 2026  
**Team:** importNumpy  
**Status:** Ready for implementation

---

## Executive Summary

A **full dashboard already exists** in `dashboard_api/` (FastAPI) and `dashboard_web/` (Next.js + React + react-globe.gl). The reason `localhost:8000` doesn't work is that `node_modules` was never installed and the dashboard runner may not have been triggered properly. 

This plan extends the existing dashboard with:
- New pipeline walkthrough pages for non-technical users
- ML diagnostic visualization integration
- Enhanced 3D globe with additional filters
- Fixed notebook execution (Q4 kernel crash)
- Complete launch automation in `run.sh`

---

## Current Dashboard State

### Existing Components
- **Backend:** `dashboard_api/main.py` (FastAPI, 241 lines, 8 endpoints)
- **Frontend:** `dashboard_web/` (Next.js 14 + React 18 + Tailwind CSS)
- **Pages:** Home (`/`), Globe (`/globe`), Phases (`/phases`), Analysis (`/analysis`)
- **3D Globe:** `react-globe.gl` with choropleth country coloring by metrics
- **API Integration:** Typed fetch helpers, country name mapping, number formatting
- **Data Sources:** DuckDB views, reports JSON/markdown, static HTML serving

### Missing Pieces
- `node_modules/` not installed in `dashboard_web/`
- Pipeline walkthrough pages for educational purposes
- ML diagnostic visualization
- Integration with Phase 5b ML results
- Proper kernel registration for notebook execution
- Dashboard launch in main `run.sh`

---

## Implementation Phases

### Phase 1: Get Existing Dashboard Running (Priority: Critical)

**Goal:** Fix launch issues and verify current dashboard works

**Steps:**
1. **Install Node dependencies**
   ```bash
   cd dashboard_web
   npm install
   ```

2. **Install dashboard Python dependencies**
   ```bash
   .venv/bin/pip install -r dashboard/requirements.txt
   ```

3. **Register kernel for notebooks**
   ```bash
   .venv/bin/python -m ipykernel install --user --name python3 --display-name "Python 3"
   ```

4. **Test launch**
   ```bash
   bash dashboard/run_local.sh
   ```
   - Verify `http://localhost:8000/api/health` → `{"ok": true}`  
   - Verify `http://localhost:3000` → home page loads with 3 nav cards

**Acceptance Criteria:**
- [ ] FastAPI server starts on port 8000 without errors
- [ ] React dev server starts on port 3000 without errors  
- [ ] Globe page renders 3D world map with country colors
- [ ] Analysis page shows iframe embeds of notebook HTML reports

---

### Phase 2: Pipeline Walkthrough Pages (Priority: High)

**Goal:** Add 8 educational pages walking users through each pipeline phase

**File Structure:**
```
dashboard_web/src/app/pipeline/
├── layout.tsx          # Sidebar nav + progress indicator
├── page.tsx            # Overview: flowchart + run metadata
├── phase1/page.tsx     # Phase 1: Ingest walkthrough
├── phase2/page.tsx     # Phase 2: Data quality walkthrough
├── phase2b/page.tsx    # Phase 2b: Synthetic signatures walkthrough
├── phase3/page.tsx     # Phase 3: Clean & transform walkthrough
├── phase4/page.tsx     # Phase 4: Analytical views walkthrough
├── phase4b/page.tsx    # Phase 4b: Robustness walkthrough
├── phase5/page.tsx     # Phase 5: Prompt gap walkthrough
└── phase5b/page.tsx    # Phase 5b: ML diagnostic walkthrough
```

**Content Strategy:**
- Source explanations from existing `docs/04_phase1_ingest.md` through `docs/11_phase5b_ml_diagnostic.md`
- Show live data counts and statuses via API calls
- Include visual progress indicators (green/red status circles)
- Link between phases with "Next Phase" navigation

**New API Endpoints Needed:**
- `GET /api/synthetic-signatures` (reads `reports/synthetic_signatures.json`)
- `GET /api/ml-diagnostic` (reads `reports/ml_diagnostic.json`)
- `GET /api/table/sample?table=raw_health&limit=20` (sample rows)
- `GET /api/table/columns?table=raw_health` (schema info)

**Acceptance Criteria:**
- [ ] `/pipeline` overview shows flowchart of all 8 phases with status indicators
- [ ] Each phase page loads relevant data from the API
- [ ] Sidebar navigation highlights current phase
- [ ] Content is written for non-technical team members
- [ ] Links connect phases in logical sequence

---

### Phase 3: ML Diagnostic Visualization (Priority: Medium)

**Goal:** Dedicated page for ML diagnostic results with charts

**Components:**
- `dashboard_web/src/app/ml-diagnostic/page.tsx`
- 4 chart visualizations using `recharts` or inline SVG

**Charts to Include:**
1. **R² Scores Bar Chart** — horizontal bars for each regression target (mortality, recovery, prevalence)
2. **Classification Accuracy** — model vs chance baseline comparison
3. **Feature Importance Distribution** — sorted bars showing uniformity across features
4. **Overall Verdict Card** — green/red styling with conclusion text

**Data Source:** `GET /api/ml-diagnostic` → `reports/ml_diagnostic.json`

**Acceptance Criteria:**
- [ ] Page loads ML diagnostic JSON without errors
- [ ] All 4 visualizations render correctly
- [ ] Charts are styled consistently with dashboard theme
- [ ] Overall verdict displays prominently with appropriate color coding

---

### Phase 4: Globe Page Enhancements (Priority: Medium)

**Goal:** Add missing filter controls and improve UX

**Enhancements:**
1. **Additional Filters** — add `disease_category`, `disease_name`, `age_group`, `gender` dropdowns (API already supports these)
2. **Color Legend** — gradient bar showing min→max value mapping
3. **Synthetic Data Warning** — dismissible banner linking to `/pipeline/phase2b`
4. **Performance** — loading states while fetching country data

**Existing Features to Preserve:**
- 3D globe with `react-globe.gl`
- Click-to-drill country details
- Metric/year/dedup controls
- Country name mapping (dataset ↔ geographic)

**Acceptance Criteria:**
- [ ] All filter dropdowns populate from `GET /api/filters`
- [ ] Filter combinations update globe colors correctly
- [ ] Color legend matches actual min/max values
- [ ] Warning banner explains synthetic nature with link to explanation

---

### Phase 5: Notebook Execution Fixes (Priority: High)

**Goal:** Resolve Q4 kernel crash and improve reliability

**Root Cause Analysis:**
- Q4 notebook execution was interrupted with `^C` (KeyboardInterrupt)
- Likely due to missing kernel registration or long execution time
- Some environments block socket creation for Jupyter kernels

**Solutions:**
1. **Add kernel registration** to `run.sh` setup phase
2. **Add `ipykernel` dependency** to `requirements.txt`
3. **Increase timeout** for Q4 specifically (uses scipy.stats which can be slow)
4. **Add explicit kernel specification** to nbconvert commands

**Code Changes:**
```bash
# In run.sh after pip install:
.venv/bin/python -m ipykernel install --user --name python3 --display-name "Python 3"

# Update nbconvert commands:
jupyter nbconvert --execute notebooks/q4_sensitivity_tiers.ipynb \
  --to html --output-dir=reports \
  --ExecutePreprocessor.timeout=600 \
  --ExecutePreprocessor.kernel_name=python3
```

**Acceptance Criteria:**
- [ ] All 9 notebooks execute successfully without `^C` interruptions
- [ ] Q4 notebook completes within 5-10 minutes
- [ ] Generated HTML reports contain full output (not truncated)
- [ ] Pipeline continues to dashboard launch after notebook completion

---

### Phase 6: Integration & Launch Automation (Priority: High)

**Goal:** Seamless one-click experience from pipeline to dashboard

**run.sh Updates:**
1. **Add dashboard step** after notebook execution
2. **Add kernel registration** in setup phase  
3. **Add dashboard dependencies** to pip install
4. **Add conditional dashboard launch** based on `RUN_DASHBOARD` flag

**Updated Pipeline Flow:**
```bash
run.sh
├── 1. Create/verify .venv
├── 2. pip install requirements.txt + dashboard/requirements.txt  
├── 3. Register python3 kernel
├── 4. python -m pipeline.run_pipeline (7 phases)
├── 5. jupyter nbconvert --execute (9 notebooks)
└── 6. bash dashboard/run_local.sh (if RUN_DASHBOARD=1)
```

**Environment Variable Control:**
- `RUN_DASHBOARD=1` (default) → launches dashboard after pipeline
- `RUN_DASHBOARD=0` → skips dashboard, pipeline only
- `DASHBOARD_API_PORT=8000` → API server port (optional)
- `DASHBOARD_WEB_PORT=3000` → React dev server port (optional)

**Acceptance Criteria:**
- [ ] `bash run.sh` completes entire pipeline + dashboard without user intervention
- [ ] Dashboard URLs printed clearly at the end
- [ ] Dashboard servers stay running until user exits (`^C`)
- [ ] Graceful cleanup kills background processes on exit

---

### Phase 7: Documentation & Maintenance (Priority: Medium)

**Goal:** Update docs to reflect new dashboard capabilities

**Files to Update:**
- `CLAUDE.md` → add Phase 5b, dashboard pages to project structure
- `docs/02_run_sh.md` → explain Step 6 (dashboard launch)
- `docs/README.md` → add dashboard documentation entry
- `Agents.md` → add dashboard drift check rules

**New Documentation:**
- `docs/15_dashboard.md` → comprehensive dashboard user guide
  - Architecture overview (FastAPI + Next.js)
  - How to launch (`RUN_DASHBOARD=1 bash run.sh`)
  - Page-by-page walkthrough
  - Troubleshooting common issues

**Acceptance Criteria:**
- [ ] All documentation reflects current pipeline order (8 phases)
- [ ] Non-technical users can follow dashboard guide
- [ ] Drift check rules prevent docs from going stale
- [ ] Agent instructions include dashboard development guidelines

---

## Dependencies & Requirements

### New Python Packages
```txt
# Add to requirements.txt:
ipykernel>=6.29
scikit-learn>=1.4
scipy>=1.12
```

### New Node Packages  
```json
// Add to dashboard_web/package.json:
"recharts": "^2.12.0"  // Optional: for ML diagnostic charts
```

### System Requirements
- **Node.js 18+** with npm (for React frontend)
- **Python 3.11+** with venv support
- **Network access** for npm install and Jupyter kernel setup
- **Socket permissions** for local server startup (not blocked by corporate firewall)

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Node.js not installed on user machines | Medium | High | Add Node.js installation check to `run.sh` with clear error message |
| Corporate firewall blocks local ports | Medium | Medium | Add environment detection and graceful fallback to HTML-only reports |
| Jupyter kernel issues in different environments | High | Medium | Multiple fallback strategies: ipykernel install, kernel name specification, socket detection |
| Large notebook execution times | Medium | Low | Increase timeouts, add progress indicators, option to skip notebook execution |
| Dashboard startup failures | Low | Medium | Comprehensive error handling and fallback to existing HTML reports |

---

## Success Metrics

### Technical Metrics
- [ ] 100% pipeline success rate (all phases complete without errors)
- [ ] Dashboard starts within 30 seconds of `bash run.sh` completion
- [ ] All 9 notebooks execute successfully on fresh installations
- [ ] API response times < 500ms for all endpoints
- [ ] Frontend build completes without warnings

### User Experience Metrics
- [ ] Non-technical team members can navigate pipeline walkthrough independently
- [ ] Dashboard provides value beyond static HTML reports
- [ ] 3D globe visualization loads within 10 seconds
- [ ] Educational content explains technical concepts clearly
- [ ] One-click setup works on Windows/WSL, macOS, Linux

---

## Next Steps

1. **Immediate (Today):** Execute Phase 1 to get existing dashboard running
2. **This Week:** Implement Phase 2 (pipeline walkthrough) and Phase 5 (notebook fixes)  
3. **Next Week:** Complete Phase 3 (ML visualization) and Phase 6 (integration)
4. **Following Week:** Documentation updates and testing on different environments

**Estimated Timeline:** 7-10 days for full implementation
**Required Resources:** 1 developer familiar with React/FastAPI, access to test environments

---

## Appendix: Existing Dashboard API Reference

### Current Endpoints
- `GET /api/health` → `{"ok": true}`
- `GET /api/run/latest` → run metadata + artifact status
- `GET /api/filters` → available filter values across all dimensions  
- `GET /api/globe/country-metric` → per-country averages for globe visualization
- `GET /api/country/summary` → detailed country statistics
- `GET /api/phases/summary` → table counts + robustness deltas
- `GET /api/markdown/{name}` → data quality and prompt gap reports
- Static mount: `/reports/*` → serves HTML notebooks and figures

### Database Tables Available
- `raw_health` (1M rows) — original CSV data
- `clean_health` (1M rows) — filtered and corrected  
- `country_summary` (20 rows) — per-country aggregates
- `cell_health` (dedup grain) — robustness analysis base
- `v_outcome_by_geography` to `v_premature_conclusions` — 6 analytical views
- `v_*_dedup` — robustness variants of all 6 views
- `robustness_delta_summary` — comparison metrics

---

**Plan Author:** GitHub Copilot  
**Review Status:** Ready for technical review and implementation prioritization