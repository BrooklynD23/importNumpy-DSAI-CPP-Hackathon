# Dashboard Implementation Handoff Prompt

**Objective:** Implement a multi-page React dashboard with 3D globe visualization and pipeline walkthrough for the importNumpy DND Spring 2026 Datathon project.

**Context:** A full FastAPI + Next.js dashboard already exists in `dashboard_api/` and `dashboard_web/` but needs fixes and extensions. The main pipeline produces DuckDB tables, reports, and notebook HTML outputs that the dashboard should visualize.

---

## Phase 1: Critical Fixes (DO THIS FIRST)

**Problem:** `localhost:8000` doesn't work because of missing Node dependencies and kernel registration issues.

### Step 1.1: Install Node Dependencies
```bash
cd dashboard_web
npm install
```
**Expected:** Creates `node_modules/` directory with ~1000+ packages, no errors.

### Step 1.2: Install Dashboard Python Dependencies  
```bash
.venv/bin/pip install -r dashboard/requirements.txt
```
**Expected:** Installs `fastapi>=0.115.0` and `uvicorn[standard]>=0.30.0`.

### Step 1.3: Register Jupyter Kernel
```bash
.venv/bin/python -m ipykernel install --user --name python3 --display-name "Python 3"
```
**Expected:** Prevents "kernel not found" errors in notebook execution.

### Step 1.4: Test Dashboard Launch
```bash
bash dashboard/run_local.sh
```
**Verify:**
- [ ] `http://localhost:8000/api/health` returns `{"ok": true}`
- [ ] `http://localhost:3000` loads home page with Globe/Phases/Analysis nav cards
- [ ] Globe page renders 3D world map (may take 10 seconds to load)
- [ ] Analysis page shows iframe embeds of notebook reports

**STOP HERE if any step fails. Fix before proceeding.**

---

## Phase 2: Fix Notebook Execution (HIGH PRIORITY)

**Problem:** Q4 notebook crashes with `KeyboardInterrupt` during `nbconvert --execute`.

### Step 2.1: Add ipykernel Dependency
Add this line to `requirements.txt`:
```
ipykernel>=6.29
```

### Step 2.2: Update run.sh Notebook Section
Find the notebook execution loop in `run.sh` and update each `jupyter nbconvert` command:

**Before:**
```bash
jupyter nbconvert --execute "notebooks/${nb}.ipynb" --to html --output-dir=reports/
```

**After:**
```bash
jupyter nbconvert --execute "notebooks/${nb}.ipynb" \
  --to html --output-dir=reports/ \
  --ExecutePreprocessor.timeout=600 \
  --ExecutePreprocessor.kernel_name=python3
```

### Step 2.3: Add Kernel Registration to run.sh
Add this line in `run.sh` after the pip install step:
```bash
echo "[SETUP] Registering Jupyter kernel..."
.venv/bin/python -m ipykernel install --user --name python3 --display-name "Python 3"
```

### Step 2.4: Test Full Pipeline
```bash
bash run.sh
```
**Expected:** All 8 notebooks execute successfully without `^C` interruptions.

---

## Phase 3: Implement ML Diagnostic Integration

**Goal:** Add Phase 5b ML diagnostic results to the dashboard.

### Step 3.1: Update Pipeline to Include Phase 5b
The ML diagnostic phase from the previous session should already be implemented. Verify `pipeline/phase5b_ml_diagnostic.py` exists and is registered in `pipeline/run_pipeline.py`.

### Step 3.2: Add ML Diagnostic API Endpoint
Add to `dashboard_api/main.py`:

```python
@app.get("/api/ml-diagnostic")
def ml_diagnostic() -> dict:
    path = KNOWN_ARTIFACTS.get("ml_diagnostic")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="ML diagnostic not found")
    
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read ML diagnostic: {e}")
```

Add `ml_diagnostic` to `KNOWN_ARTIFACTS` in `dashboard_api/settings.py`:
```python
KNOWN_ARTIFACTS = {
    # ...existing artifacts...
    "ml_diagnostic": PATHS.reports_dir / "ml_diagnostic.json",
}
```

### Step 3.3: Create ML Diagnostic Page
Create `dashboard_web/src/app/ml-diagnostic/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { apiGetJson } from "@/lib/api";

type MLDiagnosticResponse = {
  regression_probes: Array<{
    target: string;
    cv_r2_mean: number;
    cv_r2_std: number;
    verdict: string;
  }>;
  classification_probe: {
    cv_accuracy_mean: number;
    chance_accuracy: number;
    verdict: string;
  };
  overall_verdict: {
    conclusion: string;
  };
};

export default function MLDiagnostic() {
  const [data, setData] = useState<MLDiagnosticResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGetJson<MLDiagnosticResponse>("/api/ml-diagnostic")
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <div className="text-red-300">Error: {error}</div>;
  if (!data) return <div className="text-slate-300">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">ML Diagnostic: Proving Synthetic Data</h1>
        <p className="text-slate-300">
          Machine learning models trained on real health data should find meaningful patterns. 
          On synthetic data, they find nothing — proving our dataset is artificially generated.
        </p>
      </div>

      {/* R² Scores Chart */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-lg font-semibold mb-4">Regression Probes: R² Scores</h2>
        <div className="space-y-3">
          {data.regression_probes.map((probe) => (
            <div key={probe.target} className="flex items-center gap-4">
              <div className="w-32 text-sm font-mono">{probe.target}</div>
              <div className="flex-1 bg-slate-800 rounded h-6 relative">
                <div 
                  className="bg-red-500 h-full rounded"
                  style={{ width: `${Math.max(probe.cv_r2_mean * 1000, 2)}%` }}
                />
                <div className="absolute inset-0 flex items-center px-2 text-xs text-white">
                  {probe.cv_r2_mean.toFixed(4)}
                </div>
              </div>
              <div className="text-xs text-slate-400 w-48">{probe.verdict}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Classification Results */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-lg font-semibold mb-4">Disease Classification</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">
              {(data.classification_probe.cv_accuracy_mean * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-slate-300">Model Accuracy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-500">
              {(data.classification_probe.chance_accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-slate-300">Chance Baseline</div>
          </div>
        </div>
        <div className="mt-3 text-sm text-slate-400">{data.classification_probe.verdict}</div>
      </div>

      {/* Overall Verdict */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-lg font-semibold mb-3">Overall Conclusion</h2>
        <p className="text-slate-200">{data.overall_verdict.conclusion}</p>
      </div>
    </div>
  );
}
```

### Step 3.4: Add ML Diagnostic to Navigation
Update `dashboard_web/src/app/layout.tsx` to add "ML Diagnostic" to the nav:

```tsx
<nav className="flex gap-4 text-sm text-slate-200">
  <Link className="hover:text-white" href="/globe">Globe</Link>
  <Link className="hover:text-white" href="/phases">Phases</Link>
  <Link className="hover:text-white" href="/analysis">Analysis</Link>
  <Link className="hover:text-white" href="/ml-diagnostic">ML Diagnostic</Link>
</nav>
```

---

## Phase 4: Pipeline Walkthrough Pages

**Goal:** Add educational pages that walk non-technical users through each pipeline phase.

### Step 4.1: Create Pipeline Layout
Create `dashboard_web/src/app/pipeline/layout.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const phases = [
  { id: "1", name: "Ingest", path: "/pipeline/phase1" },
  { id: "2", name: "Profile", path: "/pipeline/phase2" },
  { id: "2b", name: "Synthetic", path: "/pipeline/phase2b" },
  { id: "3", name: "Clean", path: "/pipeline/phase3" },
  { id: "4", name: "Views", path: "/pipeline/phase4" },
  { id: "4b", name: "Robustness", path: "/pipeline/phase4b" },
  { id: "5", name: "Gap Matrix", path: "/pipeline/phase5" },
  { id: "5b", name: "ML Diagnostic", path: "/pipeline/phase5b" },
];

export default function PipelineLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="grid gap-4 lg:grid-cols-[250px_1fr]">
      <nav className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-3">Pipeline Phases</div>
        <div className="space-y-1">
          {phases.map((phase) => (
            <Link
              key={phase.id}
              href={phase.path}
              className={[
                "block px-3 py-2 rounded text-sm",
                pathname === phase.path
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              ].join(" ")}
            >
              Phase {phase.id}: {phase.name}
            </Link>
          ))}
        </div>
      </nav>
      <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
        {children}
      </div>
    </div>
  );
}
```

### Step 4.2: Create Pipeline Overview
Create `dashboard_web/src/app/pipeline/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { apiGetJson, type PhasesSummaryResponse } from "@/lib/api";

export default function PipelineOverview() {
  const [data, setData] = useState<PhasesSummaryResponse | null>(null);

  useEffect(() => {
    apiGetJson<PhasesSummaryResponse>("/api/phases/summary").then(setData).catch(() => {});
  }, []);

  const phases = [
    { id: "1", name: "Ingest", table: "raw_health", description: "Load CSV into DuckDB" },
    { id: "2", name: "Profile", artifact: "data_quality_report", description: "Check data quality" },
    { id: "2b", name: "Synthetic", artifact: "synthetic_signatures", description: "Detect synthetic patterns" },
    { id: "3", name: "Clean", table: "clean_health", description: "Filter and transform" },
    { id: "4", name: "Views", table: "v_outcome_by_geography", description: "Build analytical views" },
    { id: "4b", name: "Robust", table: "cell_health", description: "Robustness checks" },
    { id: "5", name: "Gap Matrix", artifact: "prompt_gap_matrix", description: "Map prompt to data" },
    { id: "5b", name: "ML Diagnostic", artifact: "ml_diagnostic", description: "Prove synthetic data" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Pipeline Overview</h1>
        <p className="text-slate-300 mt-2">
          Our data pipeline transforms raw health statistics through 8 phases, 
          each with verification gates to ensure quality.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {phases.map((phase) => {
          const isComplete = phase.table 
            ? data?.tables?.[phase.table] != null
            : data?.artifacts?.[phase.artifact]?.exists;

          return (
            <div
              key={phase.id}
              className={[
                "rounded border p-4",
                isComplete 
                  ? "border-green-600 bg-green-900/20" 
                  : "border-slate-700 bg-slate-900/40"
              ].join(" ")}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className={[
                  "w-3 h-3 rounded-full",
                  isComplete ? "bg-green-500" : "bg-slate-600"
                ].join(" ")} />
                <div className="text-sm font-semibold">Phase {phase.id}</div>
              </div>
              <div className="text-sm font-medium">{phase.name}</div>
              <div className="text-xs text-slate-400 mt-1">{phase.description}</div>
            </div>
          );
        })}
      </div>

      {data?.run ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
          <div className="text-sm font-semibold">Latest Run</div>
          <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
            <div>
              <div className="text-slate-400">Generated</div>
              <div className="font-mono">{data.run.generated_at || 'Unknown'}</div>
            </div>
            <div>
              <div className="text-slate-400">Duration</div>
              <div className="font-mono">{data.run.total_seconds}s</div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
```

### Step 4.3: Create Individual Phase Pages
Create these files with basic content (you can expand later):

**`dashboard_web/src/app/pipeline/phase1/page.tsx`:**
```tsx
export default function Phase1() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 1: Data Ingest</h1>
      <p className="text-slate-300">
        Reads the raw CSV file (1M rows × 25 columns) and loads it into DuckDB as the `raw_health` table.
        Also adds computed columns: `urbanization_tier` and `resource_index`.
      </p>
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="mt-2 text-sm text-slate-300 space-y-1">
          <li>• DuckDB table: `raw_health` (1,000,000 rows)</li>
          <li>• Added `urbanization_tier` column (Rural/Peri-urban/Urban)</li>
          <li>• Added `resource_index` composite score</li>
        </ul>
      </div>
    </div>
  );
}
```

Create similar files for `phase2/page.tsx`, `phase2b/page.tsx`, etc. with appropriate content.

### Step 4.4: Add Pipeline to Main Navigation
Update the main nav in `dashboard_web/src/app/layout.tsx`:

```tsx
<nav className="flex gap-4 text-sm text-slate-200">
  <Link className="hover:text-white" href="/globe">Globe</Link>
  <Link className="hover:text-white" href="/pipeline">Pipeline</Link>
  <Link className="hover:text-white" href="/phases">Phases</Link>
  <Link className="hover:text-white" href="/analysis">Analysis</Link>
  <Link className="hover:text-white" href="/ml-diagnostic">ML Diagnostic</Link>
</nav>
```

---

## Phase 5: Dashboard Launch in run.sh

**Goal:** Automatically start dashboard after pipeline completion.

### Step 5.1: Update run.sh
Add this section at the end of `run.sh` (after notebook execution):

```bash
# ── Step 5: Dashboard (optional) ──────────────────────────────────────────────
if [ "${RUN_DASHBOARD:-1}" = "1" ]; then
    echo ""
    echo "========================================"
    echo " Starting Dashboard"
    echo "========================================"
    echo ""
    echo "  API Server:  http://localhost:8000"
    echo "  Web App:     http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop all servers."
    
    # Launch dashboard in foreground (blocks until user exits)
    bash dashboard/run_local.sh
else
    echo ""
    echo "========================================"
    echo " Pipeline Complete"
    echo "========================================"
    echo ""
    echo "To view dashboard: bash dashboard/run_local.sh"
fi
```

---

## Acceptance Criteria & Testing

**Test each phase independently:**

1. **Phase 1 Complete:** Dashboard loads at `localhost:3000`, globe shows country colors
2. **Phase 2 Complete:** All 8 notebooks execute without errors in `bash run.sh`  
3. **Phase 3 Complete:** ML Diagnostic page shows charts and verdict
4. **Phase 4 Complete:** Pipeline walkthrough pages load with phase nav sidebar
5. **Phase 5 Complete:** `bash run.sh` automatically launches dashboard

**Final Integration Test:**
```bash
# Clean start
rm -rf .venv dashboard_web/node_modules
bash run.sh
```
**Expected:** Complete pipeline → notebook HTML generation → dashboard auto-launch → all pages functional.

---

## Common Issues & Solutions

**"npm not found":** Install Node.js 18+ first  
**"Port 8000 in use":** Kill existing process with `lsof -ti:8000 | xargs kill`  
**"Jupyter kernel not found":** Run kernel registration step manually  
**Globe not loading:** Check browser console for WebGL errors, try different browser  
**API 500 errors:** Check that `data/health.duckdb` exists and reports are generated  

---

## Files You'll Modify

**Critical Files:**
- `run.sh` (add kernel registration, dashboard launch)
- `requirements.txt` (add ipykernel)
- `dashboard_api/main.py` (add ML diagnostic endpoint)
- `dashboard_api/settings.py` (add ML diagnostic to artifacts)

**New Files:**
- `dashboard_web/src/app/ml-diagnostic/page.tsx`
- `dashboard_web/src/app/pipeline/layout.tsx`  
- `dashboard_web/src/app/pipeline/page.tsx`
- `dashboard_web/src/app/pipeline/phase*/page.tsx` (8 files)

**Expected Time:** 4-6 hours for experienced React/FastAPI developer

---

**SUCCESS METRIC:** Non-technical team members can run `bash run.sh`, wait for completion, then explore the entire pipeline through the web dashboard without needing to understand code or databases.