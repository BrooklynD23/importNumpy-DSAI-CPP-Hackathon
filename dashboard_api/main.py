from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dashboard_api import db
from dashboard_api.geo import resolve_country, get_resolve_stats
from dashboard_api.settings import CORS_ORIGINS, KNOWN_ARTIFACTS, MARKDOWN_ALLOWLIST, PATHS


def _file_info(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "path": str(path), "mtime": None, "size": None}
    stat = path.stat()
    return {
        "exists": True,
        "path": str(path),
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "size": stat.st_size,
    }


def _best_effort_read_json(path: Path) -> dict | None:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_run_meta() -> dict | None:
    meta = _best_effort_read_json(KNOWN_ARTIFACTS["run_metadata"])
    if meta is not None:
        meta["_source"] = "reports/_run_metadata.json"
        return meta

    # Fallback: infer "latest" from mtimes of known artifacts + DB file
    candidates = [PATHS.db_path, *KNOWN_ARTIFACTS.values()]
    existing = [p for p in candidates if p.exists()]
    if not existing:
        return None

    latest = max(existing, key=lambda p: p.stat().st_mtime)
    return {
        "generated_at": datetime.fromtimestamp(latest.stat().st_mtime).isoformat(),
        "_source": f"mtime_fallback:{latest.name}",
    }


app = FastAPI(
    title="importNumpy Dashboard API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if PATHS.reports_dir.exists():
    app.mount(
        "/reports",
        StaticFiles(directory=str(PATHS.reports_dir), html=True),
        name="reports",
    )


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/run/latest")
def latest_run() -> dict:
    run_meta = _resolve_run_meta()
    artifacts = {k: _file_info(p) for k, p in KNOWN_ARTIFACTS.items()}
    return {
        "run": run_meta,
        "db_path": str(PATHS.db_path),
        "reports_dir": str(PATHS.reports_dir),
        "artifacts": artifacts,
    }


@app.get("/api/filters")
def filters() -> dict:
    try:
        con = db.connect()
        try:
            return db.get_filter_domains(con)
        finally:
            con.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/globe/country-metric")
def globe_country_metric(
    metric: str,
    year: int | None = Query(default=None),
    disease_category: str | None = Query(default=None),
    disease_name: str | None = Query(default=None),
    age_group: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    dedup: bool = Query(default=False),
) -> dict:
    try:
        con = db.connect()
        try:
            filters_obj = db.Filters(
                year=year,
                disease_category=disease_category,
                disease_name=disease_name,
                age_group=age_group,
                gender=gender,
            )
            rows = db.get_country_metric(
                con,
                metric=metric,
                dedup=dedup,
                filters=filters_obj,
            )
        finally:
            con.close()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    values = [r["value"] for r in rows if r["value"] is not None]
    vmin = min(values) if values else None
    vmax = max(values) if values else None

    return {
        "metric": metric,
        "dedup": dedup,
        "filters": {
            "year": year,
            "disease_category": disease_category,
            "disease_name": disease_name,
            "age_group": age_group,
            "gender": gender,
        },
        "min": vmin,
        "max": vmax,
        "data": rows,
    }


@app.get("/api/globe/country-points")
def globe_country_points(
    metric: str,
    year: int | None = Query(default=None),
    disease_category: str | None = Query(default=None),
    disease_name: str | None = Query(default=None),
    age_group: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    dedup: bool = Query(default=False),
) -> dict:
    """Return point-ready rows with ISO3 + lat/lon for globe markers."""
    try:
        con = db.connect()
        try:
            filters_obj = db.Filters(
                year=year,
                disease_category=disease_category,
                disease_name=disease_name,
                age_group=age_group,
                gender=gender,
            )
            rows = db.get_country_metric(
                con,
                metric=metric,
                dedup=dedup,
                filters=filters_obj,
            )
        finally:
            con.close()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Enrich rows with ISO3 + centroid coordinates
    enriched: list[dict] = []
    for row in rows:
        geo = resolve_country(row["country"])
        if geo is None:
            continue
        enriched.append({
            "iso3": geo["iso3"],
            "country": row["country"],
            "lat": geo["lat"],
            "lon": geo["lon"],
            "value": row["value"],
            "n_rows": row["n_rows"],
        })

    # Compute min/max over resolved rows with numeric values only
    numeric_vals = [r["value"] for r in enriched if r["value"] is not None]
    vmin = min(numeric_vals) if numeric_vals else None
    vmax = max(numeric_vals) if numeric_vals else None

    return {
        "metric": metric,
        "dedup": dedup,
        "filters": {
            "year": year,
            "disease_category": disease_category,
            "disease_name": disease_name,
            "age_group": age_group,
            "gender": gender,
        },
        "min": vmin,
        "max": vmax,
        "data": enriched,
        "resolve_stats": get_resolve_stats(),
    }


@app.get("/api/country/summary")
def country_summary(
    country: str,
    year: int | None = Query(default=None),
    disease_category: str | None = Query(default=None),
    disease_name: str | None = Query(default=None),
    age_group: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    dedup: bool = Query(default=False),
) -> dict:
    try:
        con = db.connect()
        try:
            filters_obj = db.Filters(
                year=year,
                disease_category=disease_category,
                disease_name=disease_name,
                age_group=age_group,
                gender=gender,
            )
            payload = db.get_country_summary(
                con,
                country=country,
                dedup=dedup,
                filters=filters_obj,
            )
        finally:
            con.close()
        return payload
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phases/summary")
def phases_summary() -> dict:
    try:
        con = db.connect()
        try:
            table_counts = db.get_table_counts(
                con,
                [
                    "raw_health",
                    "clean_health",
                    "country_summary",
                    "cell_health",
                    "v_outcome_by_geography",
                    "v_access_vs_outcomes",
                    "v_outlier_communities",
                    "v_sensitivity_tiers",
                    "v_sparse_reporting",
                    "v_premature_conclusions",
                    "robustness_delta_summary",
                ],
            )
            robustness = db.get_robustness_summary(con)
        finally:
            con.close()

        artifacts = {k: _file_info(p) for k, p in KNOWN_ARTIFACTS.items()}
        run_meta = _resolve_run_meta()

        return {
            "run": run_meta,
            "artifacts": artifacts,
            "tables": table_counts,
            "robustness_delta_summary": robustness,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/markdown/{name}")
def get_markdown(name: str) -> dict:
    if name not in MARKDOWN_ALLOWLIST:
        raise HTTPException(status_code=404, detail="Unknown markdown artifact")
    path = MARKDOWN_ALLOWLIST[name]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Missing {path}")
    return {"name": name, "path": str(path), "markdown": path.read_text(encoding="utf-8")}


@app.get("/api/ml-diagnostic")
def ml_diagnostic() -> dict:
    path = KNOWN_ARTIFACTS.get("ml_diagnostic")
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="ML diagnostic not found — run pipeline first")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read ML diagnostic: {e}")
