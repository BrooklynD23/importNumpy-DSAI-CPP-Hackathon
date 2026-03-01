#!/usr/bin/env bash
# ============================================================================
# DND Spring 2026 Datathon — One-Click Pipeline Runner
# Double-click this file (or run: bash run.sh) to execute the full pipeline.
# ============================================================================
set -euo pipefail

# ─── Colours ────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

print_step()  { echo -e "\n${CYAN}${BOLD}▶ $1${RESET}"; }
print_ok()    { echo -e "${GREEN}✔ $1${RESET}"; }
print_warn()  { echo -e "${YELLOW}⚠ $1${RESET}"; }

# ─── Spinner — show animated dots while a background PID runs ────────────────
spinner() {
  local pid=$1 msg="${2:-Working}"
  local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
  local i=0
  # Only animate when attached to a terminal
  if [ -t 1 ]; then
    tput civis 2>/dev/null || true          # hide cursor
    while kill -0 "$pid" 2>/dev/null; do
      printf "\r  ${CYAN}%s${RESET}  %s  " "${frames[$i]}" "$msg"
      i=$(( (i + 1) % ${#frames[@]} ))
      sleep 0.1
    done
    printf "\r\033[K"                       # clear spinner line
    tput cnorm 2>/dev/null || true          # restore cursor
  else
    wait "$pid"
  fi
}

# ─── Hash helper — SHA256 of a file (portable: sha256sum or shasum) ──────────
file_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    # Fallback: use mtime so we at least detect changes
    stat -c '%Y' "$1" 2>/dev/null || stat -f '%m' "$1" 2>/dev/null || echo "0"
  fi
}

# ─── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV=".venv"
REPORTS_DIR="reports"
DB_FILE="data/health.duckdb"

# Key output sentinels to decide if pipeline has run before
SENTINEL_DB="$DB_FILE"
SENTINEL_REPORT="$REPORTS_DIR/data_quality_report.md"
SENTINEL_ML="$REPORTS_DIR/ml_diagnostic.json"
SENTINEL_NOTEBOOKS=(
  "$REPORTS_DIR/q1_outcome_geography.html"
  "$REPORTS_DIR/q2_access_vs_outcomes.html"
  "$REPORTS_DIR/q3_outlier_communities.html"
  "$REPORTS_DIR/q4_sensitivity_tiers.html"
  "$REPORTS_DIR/q5_sparse_reporting.html"
  "$REPORTS_DIR/q6_premature_conclusions.html"
  "$REPORTS_DIR/benchmark_comparison.html"
  "$REPORTS_DIR/summary_executive.html"
)

# ─── Check for existing outputs ──────────────────────────────────────────────
outputs_exist() {
  [[ -f "$SENTINEL_DB" && -f "$SENTINEL_REPORT" ]]
}

notebooks_exist() {
  for f in "${SENTINEL_NOTEBOOKS[@]}"; do
    [[ -f "$f" ]] || return 1
  done
  return 0
}

# ─── Prompt user if outputs already exist ────────────────────────────────────
RUN_PIPELINE=1
RUN_NOTEBOOKS=1

if outputs_exist; then
  echo ""
  echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
  echo -e "${GREEN}${BOLD}  Previous pipeline outputs detected!${RESET}"
  echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
  echo ""
  echo -e "  ${CYAN}[1]${RESET} Re-run full pipeline + notebooks  ${YELLOW}(~10-20 min)${RESET}"
  echo -e "  ${CYAN}[2]${RESET} Re-run pipeline only (skip notebooks) ${YELLOW}(~2-5 min)${RESET}"
  if notebooks_exist; then
    echo -e "  ${CYAN}[3]${RESET} Skip everything — just launch dashboard ${GREEN}(instant)${RESET}"
  fi
  echo -e "  ${CYAN}[4]${RESET} Re-run notebooks only (keep existing DB) ${YELLOW}(~5-15 min)${RESET}"
  echo ""
  printf "${BOLD}Your choice [1/2/3/4]: ${RESET}"
  read -r choice </dev/tty

  case "$choice" in
    1)
      print_ok "Full re-run selected."
      RUN_PIPELINE=1; RUN_NOTEBOOKS=1
      ;;
    2)
      print_ok "Pipeline only — notebooks will be skipped."
      RUN_PIPELINE=1; RUN_NOTEBOOKS=0
      ;;
    3)
      if notebooks_exist; then
        print_ok "Skipping pipeline & notebooks — launching dashboard from last data."
        RUN_PIPELINE=0; RUN_NOTEBOOKS=0
      else
        print_warn "Some notebook outputs are missing. Falling back to full re-run."
        RUN_PIPELINE=1; RUN_NOTEBOOKS=1
      fi
      ;;
    4)
      print_ok "Notebooks only — existing database will be reused."
      RUN_PIPELINE=0; RUN_NOTEBOOKS=1
      ;;
    *)
      print_warn "Unrecognised input — defaulting to full re-run."
      RUN_PIPELINE=1; RUN_NOTEBOOKS=1
      ;;
  esac
else
  print_step "No previous outputs found — running full pipeline."
fi

# ── Step 1: Ensure Python virtual environment exists ──────────────────────────
print_step "Setting up Python environment"
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
    print_ok "Created .venv"
else
    print_ok ".venv already exists"
fi

# ── Step 2: Install dependencies ──────────────────────────────────────────────
print_step "Checking dependencies"

STAMP_FILE="$VENV/.pip_stamp"
REQ_HASH="$(file_hash requirements.txt 2>/dev/null || echo 'none')"
SAVED_HASH="$(cat "$STAMP_FILE" 2>/dev/null || echo '')"

if [ "$REQ_HASH" = "$SAVED_HASH" ] && [ -f "$VENV/bin/pip" ]; then
    print_ok "Dependencies already up-to-date (requirements.txt unchanged)"
else
    echo -e "  ${YELLOW}requirements.txt changed or first install — installing packages...${RESET}"
    # Count packages so the label is informative
    PKG_COUNT=$(grep -cE '^\s*[^#\s]' requirements.txt 2>/dev/null || echo '?')
    .venv/bin/pip install --quiet -r requirements.txt &
    PIP_PID=$!
    spinner $PIP_PID "Installing ${PKG_COUNT} packages (this may take a minute on first run)"
    wait $PIP_PID
    # Save hash so next run skips install
    echo "$REQ_HASH" > "$STAMP_FILE"
    print_ok "Dependencies installed"
fi

# Register Jupyter kernel only if not already present
KERNEL_DIR="${HOME}/.local/share/jupyter/kernels/python3"
if [ ! -d "$KERNEL_DIR" ]; then
    .venv/bin/python -m ipykernel install --user --name python3 --display-name "Python 3" 2>/dev/null || true
    print_ok "Jupyter kernel registered"
else
    print_ok "Jupyter kernel already registered"
fi

# ── Step 3: Run the data pipeline ─────────────────────────────────────────────
if [ "$RUN_PIPELINE" -eq 1 ]; then
    print_step "Running data pipeline (all phases)"
    .venv/bin/python -m pipeline.run_pipeline
    print_ok "Pipeline complete"
else
    print_ok "Pipeline skipped — using existing outputs"
fi

# ── Step 4: Run analysis notebooks ─────────────────────────────────────────
if [ "$RUN_NOTEBOOKS" -eq 1 ]; then
    print_step "Executing notebooks → HTML reports"

    # Check socket support (needed for Jupyter kernel communication)
    NOTEBOOKS_ENABLED=1
    if ! .venv/bin/python - <<'PY' 2>/dev/null; then
import socket
s = socket.socket()
s.close()
PY
        print_warn "This environment cannot open local sockets — skipping notebooks."
        NOTEBOOKS_ENABLED=0
    fi

    if [ "$NOTEBOOKS_ENABLED" -eq 1 ]; then
        mkdir -p reports/figures
        for nb in q1_outcome_geography q2_access_vs_outcomes q3_outlier_communities \
                  q4_sensitivity_tiers q5_sparse_reporting q6_premature_conclusions \
                  benchmark_comparison summary_executive; do
            echo -e "  ${CYAN}→${RESET} $nb"
            .venv/bin/jupyter nbconvert --execute "notebooks/${nb}.ipynb" \
                --to html --output-dir=reports/ \
                --ExecutePreprocessor.timeout=600 \
                --ExecutePreprocessor.kernel_name=python3 2>&1
        done
        print_ok "All notebooks executed"
    fi
else
    print_ok "Notebooks skipped — using existing HTML reports"
fi

# ── Step 5: Build PowerPoint presentation ────────────────────────────────────
print_step "Building PowerPoint presentation"
if [ -f "presentation/build_slides.py" ]; then
    mkdir -p presentation
    .venv/bin/python presentation/build_slides.py
    print_ok "Presentation saved: presentation/DND_2026_importNumpy.pptx"
else
    print_warn "presentation/build_slides.py not found — skipping slide build"
fi

# ── Step 6: Dashboard ────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  All done!${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "  Reports:   ${CYAN}$REPORTS_DIR/${RESET}"
echo -e "  Database:  ${CYAN}$DB_FILE${RESET}"
echo ""

# Default: launch dashboard on local machines, skip in CI
RUN_DASHBOARD_DEFAULT=1
if [ -n "${CI:-}" ]; then
    RUN_DASHBOARD_DEFAULT=0
fi
RUN_DASHBOARD="${RUN_DASHBOARD:-$RUN_DASHBOARD_DEFAULT}"

if [ "$RUN_DASHBOARD" -eq 1 ] && [ -f "dashboard/run_local.sh" ]; then
    print_step "Starting local dashboard (Ctrl+C to stop)"
    echo -e "  API:  ${CYAN}http://localhost:8000${RESET}"
    echo -e "  Web:  ${CYAN}http://localhost:3000${RESET}"
    echo ""
    if ! bash dashboard/run_local.sh; then
        print_warn "Dashboard failed to start (optional; pipeline outputs are complete)."
    fi
else
    echo -e "  To launch dashboard: ${YELLOW}RUN_DASHBOARD=1 bash run.sh${RESET}"
fi
