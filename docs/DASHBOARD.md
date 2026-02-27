# Local Dashboard (Globe + Phase-by-Phase + Analysis)

This repo includes a local dashboard that always reads from the **most recent pipeline run**.

## What it shows
- **3D globe choropleth**: per-country metrics from DuckDB (optionally dedup robustness view).
- **Phase dashboard**: table counts + report artifacts + robustness deltas.
- **Analysis overview**: embeds/links the notebook HTML outputs in `reports/`.

## Prerequisites
- Run the pipeline at least once: `bash run.sh`
- Node.js (for the web UI)

## Start the dashboard

```bash
bash dashboard/run_local.sh
```

Or run everything (pipeline + dashboard):

```bash
bash run.sh
```

Then open:
- Web UI: `http://localhost:3000`
- API: `http://localhost:8000/api/health`
- Reports static: `http://localhost:8000/reports/`

## “Most recent run” definition
- Primary source of truth: `reports/_run_metadata.json` (written by `pipeline/run_pipeline.py`).
- Data source: `data/health.duckdb`
- Judge-facing artifacts: `reports/*.md`, `reports/*.json`, and `reports/*.html`
