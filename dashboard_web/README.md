# Dashboard Web (Next.js)

This is a local frontend for exploring the latest pipeline run (3D globe + phase dashboard + analysis).

## Run (recommended)

From the repo root:

```bash
bash dashboard/run_local.sh
```

## Run (manual)

Terminal 1 (API):

```bash
.venv/bin/uvicorn dashboard_api.main:app --reload --port 8000
```

Terminal 2 (Web):

```bash
cd dashboard_web
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev -- --port 3000
```

