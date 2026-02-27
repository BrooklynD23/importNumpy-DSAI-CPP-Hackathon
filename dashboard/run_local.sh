#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

API_PORT="${DASHBOARD_API_PORT:-8000}"
WEB_PORT="${DASHBOARD_WEB_PORT:-3000}"

echo "========================================"
echo " importNumpy — Local Dashboard"
echo "========================================"

if [ ! -d ".venv" ]; then
  echo "[SETUP] Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "[SETUP] Installing Python dependencies..."
if ! .venv/bin/pip install --quiet -r requirements.txt -r dashboard/requirements.txt; then
  echo "[DASHBOARD] WARNING: Failed to install dashboard dependencies (offline or restricted network)."
  echo "[DASHBOARD] Skipping dashboard startup. Re-run on a machine with internet access."
  exit 0
fi

# NOTE: The API + Next.js dev server require opening local sockets.
# Some restricted environments block socket creation entirely.
if ! .venv/bin/python - <<'PY' 2>/dev/null; then
import socket
s = socket.socket()
s.close()
PY
  echo "[DASHBOARD] WARNING: This environment cannot open local sockets (server startup blocked)."
  echo "[DASHBOARD] Skipping dashboard startup. Run on a normal local machine."
  exit 0
fi

# ── Free a port if something is already listening on it ───────────────────────
free_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti tcp:"${port}" | xargs -r kill -9 2>/dev/null || true
  fi
  # Give the OS a moment to release the socket
  sleep 0.5
}

echo "[API] Freeing port ${API_PORT} if in use..."
free_port "${API_PORT}"

echo "[API] Starting dashboard API on http://0.0.0.0:${API_PORT}"
.venv/bin/uvicorn dashboard_api.main:app --reload --host 0.0.0.0 --port "${API_PORT}" &
API_PID=$!

cleanup() {
  if kill -0 "${API_PID}" >/dev/null 2>&1; then
    kill "${API_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

sleep 0.6
if ! kill -0 "${API_PID}" >/dev/null 2>&1; then
  echo "[API] ERROR: API failed to start (port in use or socket blocked)."
  exit 0
fi

# ── Detect WSL2 and resolve the API URL for Next.js ─────────────────────────
# When running inside WSL2, Windows can't reach WSL's localhost:8000 directly.
# We detect the WSL IP so the Next.js server (whether in WSL or Windows) can
# proxy to the correct address.
BACKEND_URL="http://localhost:${API_PORT}"

if grep -qi microsoft /proc/version 2>/dev/null; then
  # Running inside WSL — get the WSL2 IP for Windows-side processes
  WSL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  if [ -n "$WSL_IP" ]; then
    BACKEND_URL="http://${WSL_IP}:${API_PORT}"
    echo "[NET] Detected WSL2 — API reachable at ${BACKEND_URL}"
  fi
fi

echo "[WEB] Freeing port ${WEB_PORT} if in use..."
free_port "${WEB_PORT}"

# ── Start Next.js — prefer WSL node, fall back to Windows node ──────────────
if command -v npm >/dev/null 2>&1; then
  # Node.js available in current environment (WSL or native)
  echo "[WEB] Starting dashboard web on http://localhost:${WEB_PORT}"
  cd dashboard_web
  if [ ! -d "node_modules" ]; then
    echo "[WEB] Installing Node dependencies (first run)..."
    npm install
  fi
  export BACKEND_URL
  export NEXT_PUBLIC_API_BASE_URL="${BACKEND_URL}"
  npm run dev -- --port "${WEB_PORT}"

elif command -v powershell.exe >/dev/null 2>&1; then
  # WSL2 without Node — launch Next.js via Windows PowerShell
  echo "[WEB] Node.js not in WSL — starting Next.js via Windows PowerShell..."

  # Free port on the Windows side too
  powershell.exe -NoProfile -Command \
    "Get-NetTCPConnection -LocalPort ${WEB_PORT} -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id \$_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>/dev/null || true
  sleep 0.5

  WIN_PROJECT="$(wslpath -w "$PROJECT_ROOT")"
  echo "[WEB] Starting dashboard web on http://localhost:${WEB_PORT}"

  # Start Next.js on Windows with BACKEND_URL env var
  powershell.exe -NoProfile -Command "
    \$env:BACKEND_URL = '${BACKEND_URL}';
    \$env:NEXT_PUBLIC_API_BASE_URL = '${BACKEND_URL}';
    Set-Location '${WIN_PROJECT}\\dashboard_web';
    npx next dev --port ${WEB_PORT}
  "
else
  echo "[WEB] npm not found. Install Node.js, then run:"
  echo "      cd dashboard_web && npm install && npm run dev"
  echo "[WEB] API is still running at ${BACKEND_URL}"
  wait "$API_PID"
fi
