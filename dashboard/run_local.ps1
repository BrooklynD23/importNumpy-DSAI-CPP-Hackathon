<#
.SYNOPSIS
  Start the importNumpy dashboard from Windows PowerShell.
  Launches the FastAPI backend inside WSL and the Next.js frontend on Windows.
.USAGE
  .\dashboard\run_local.ps1
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$ApiPort  = if ($env:DASHBOARD_API_PORT) { $env:DASHBOARD_API_PORT } else { "8000" }
$WebPort  = if ($env:DASHBOARD_WEB_PORT) { $env:DASHBOARD_WEB_PORT } else { "3000" }
$WebDir   = Join-Path $ProjectRoot "dashboard_web"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " importNumpy - Local Dashboard (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Free ports ─────────────────────────────────────────────────────────────
function Free-Port([int]$port) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
    }
    # Also kill inside WSL
    wsl bash -c "fuser -k $port/tcp 2>/dev/null; true" 2>$null
    Start-Sleep -Milliseconds 500
}

Write-Host "[SETUP] Freeing ports $ApiPort and $WebPort..." -ForegroundColor DarkGray
Free-Port $ApiPort
Free-Port $WebPort

# ── 2. Start FastAPI backend in WSL ───────────────────────────────────────────
$WslProjectPath = wsl bash -c "wslpath '$($ProjectRoot -replace '\\','/')'"
$WslProjectPath = $WslProjectPath.Trim()

Write-Host "[API] Starting FastAPI backend in WSL on port $ApiPort..." -ForegroundColor Yellow

# Start the API as a background job so we can capture output
$apiJob = Start-Job -ScriptBlock {
    param($wslPath, $port)
    wsl bash -c "cd $wslPath && .venv/bin/uvicorn dashboard_api.main:app --host 0.0.0.0 --port $port 2>&1"
} -ArgumentList $WslProjectPath, $ApiPort

# Wait for the API to come up
Write-Host "[API] Waiting for API to start..." -ForegroundColor DarkGray
$BackendUrl = $null
$maxWait = 15
for ($i = 0; $i -lt $maxWait; $i++) {
    Start-Sleep -Seconds 1

    # Try localhost first (WSL2 port forwarding)
    try {
        $null = Invoke-RestMethod "http://localhost:${ApiPort}/api/health" -TimeoutSec 2
        $BackendUrl = "http://localhost:${ApiPort}"
        Write-Host "[API] Reachable at $BackendUrl (localhost forwarding)" -ForegroundColor Green
        break
    } catch {}

    # Fallback: use WSL2 IP directly
    $wslIp = (wsl bash -c "hostname -I 2>/dev/null" | Out-String).Trim().Split()[0]
    if ($wslIp) {
        try {
            $null = Invoke-RestMethod "http://${wslIp}:${ApiPort}/api/health" -TimeoutSec 2
            $BackendUrl = "http://${wslIp}:${ApiPort}"
            Write-Host "[API] Reachable at $BackendUrl (WSL2 IP)" -ForegroundColor Green
            break
        } catch {}
    }

    Write-Host "[API]   ...waiting ($($i+1)/${maxWait}s)" -ForegroundColor DarkGray
}

if (-not $BackendUrl) {
    Write-Host "[API] ERROR: Backend did not start within ${maxWait}s." -ForegroundColor Red
    Write-Host "[API] Check that .venv exists and pipeline dependencies are installed." -ForegroundColor Red
    Receive-Job $apiJob -ErrorAction SilentlyContinue | Write-Host
    Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
    exit 1
}

# ── 3. Install Node dependencies if needed ────────────────────────────────────
Set-Location $WebDir
if (-not (Test-Path "node_modules")) {
    Write-Host "[WEB] Installing Node dependencies..." -ForegroundColor Yellow
    npm install
}

# ── 4. Start Next.js dev server ───────────────────────────────────────────────
Write-Host ""
Write-Host "[WEB] Starting Next.js on http://localhost:${WebPort}" -ForegroundColor Yellow
Write-Host "[WEB] BACKEND_URL = $BackendUrl" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Dashboard:  http://localhost:${WebPort}" -ForegroundColor Green
Write-Host "  API:        ${BackendUrl}" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

$env:BACKEND_URL = $BackendUrl
$env:NEXT_PUBLIC_API_BASE_URL = ""   # Client calls go through Next.js proxy (rewrites)

try {
    npx next dev --port $WebPort
} finally {
    # Clean up the API job when Next.js stops
    Write-Host ""
    Write-Host "[CLEANUP] Stopping API..." -ForegroundColor DarkGray
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
    wsl bash -c "fuser -k ${ApiPort}/tcp 2>/dev/null; true" 2>$null
    Write-Host "[CLEANUP] Done." -ForegroundColor DarkGray
}
