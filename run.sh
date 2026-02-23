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

# ── Done ──────────────────────────────────────────────────────────────────────
echo "========================================"
echo " Pipeline finished!"
echo ""
echo " Outputs:"
echo "   Database:  data/health.duckdb"
echo "   Reports:   reports/data_quality_report.md"
echo "              reports/assumption_log.csv"
echo "========================================"
