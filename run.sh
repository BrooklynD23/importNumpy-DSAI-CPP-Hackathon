#!/usr/bin/env bash
# ============================================================================
# DND Spring 2026 Datathon — One-Click Pipeline Runner
# Double-click this file (or run: bash run.sh) to execute the full pipeline.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " DND Datathon — Data Pipeline"
echo "========================================"
echo ""

# ── Step 1: Ensure Python virtual environment exists ──────────────────────────
if [ ! -d ".venv" ]; then
    echo "[SETUP] Creating Python virtual environment..."
    python3 -m venv .venv
    echo "[SETUP] Virtual environment created."
else
    echo "[SETUP] Virtual environment found."
fi

# ── Step 2: Install dependencies ──────────────────────────────────────────────
echo "[SETUP] Installing dependencies..."
.venv/bin/pip install --quiet -r requirements.txt
echo "[SETUP] Dependencies installed."
echo ""

# ── Step 3: Run the data pipeline ─────────────────────────────────────────────
echo "[PIPELINE] Starting data pipeline..."
echo ""
.venv/bin/python -m pipeline.run_pipeline
echo ""

# ── Step 4: Run analysis notebooks ─────────────────────────────────────────
echo "[NOTEBOOKS] Running analysis notebooks..."

# NOTE: Jupyter execution requires opening local sockets for kernel communication.
# Some restricted environments (e.g., hardened sandboxes) block socket creation.
# Detect this early and skip notebooks with a clear message rather than crashing.
NOTEBOOKS_ENABLED=1
if ! .venv/bin/python - <<'PY' 2>/dev/null; then
import socket
s = socket.socket()
s.close()
PY
    echo "[NOTEBOOKS] WARNING: This environment cannot open local sockets (kernel launch blocked)."
    echo "[NOTEBOOKS] Skipping notebook execution. Run on a normal local machine to regenerate reports/*.html."
    echo ""
    NOTEBOOKS_ENABLED=0
fi

if [ "$NOTEBOOKS_ENABLED" -eq 1 ]; then
    mkdir -p reports/figures
    for nb in q1_outcome_geography q2_access_vs_outcomes q3_outlier_communities \
              q4_sensitivity_tiers q5_sparse_reporting q6_premature_conclusions \
              benchmark_comparison summary_executive; do
        echo "[NOTEBOOK] Running $nb..."
        .venv/bin/jupyter nbconvert --execute "notebooks/${nb}.ipynb" \
            --to html --output-dir=reports/ \
            --ExecutePreprocessor.timeout=300 2>&1
    done
    echo "[NOTEBOOKS] All notebooks executed."
    echo ""
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo "========================================"
echo " Pipeline finished!"
echo ""
echo " Outputs:"
echo "   Database:  data/health.duckdb"
echo "   Reports:   reports/data_quality_report.md"
echo "              reports/assumption_log.csv"
echo "              reports/synthetic_signatures.json"
echo "              reports/prompt_gap_matrix.md"
echo "              reports/q*.html (notebook outputs)"
echo "              reports/benchmark_comparison.html"
echo "              reports/summary_executive.html"
echo "   Figures:   reports/figures/*.png"
echo "========================================"
