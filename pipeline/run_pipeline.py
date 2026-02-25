"""Pipeline orchestrator — runs phases 1→2→2b→3→4→4b→5 with verification gates."""

import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import duckdb
from importlib import metadata

from pipeline import phase1_ingest, phase2_profile, phase3_clean, phase4_views
from pipeline import phase2b_synthetic_signatures
from pipeline import phase4b_robust_views
from pipeline import phase5_prompt_gap_matrix
from pipeline.config import DB_PATH, PROJECT_ROOT, REPORTS_DIR


def _best_effort_git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


def _best_effort_pkg_version(dist_name: str) -> str | None:
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return None


def _write_run_metadata(total_seconds: float) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "_run_metadata.json"

    try:
        db_path = str(DB_PATH.relative_to(PROJECT_ROOT))
    except ValueError:
        db_path = str(DB_PATH)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _best_effort_git_commit(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "total_seconds": total_seconds,
        "db_path": db_path,
        "packages": {
            "duckdb": _best_effort_pkg_version("duckdb"),
            "numpy": _best_effort_pkg_version("numpy"),
            "pandas": _best_effort_pkg_version("pandas"),
            "scipy": _best_effort_pkg_version("scipy"),
        },
    }

    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Run metadata written to {out_path}")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    phases = [
        ("Phase 1: Ingest CSV → raw_health", phase1_ingest),
        ("Phase 2: Data Quality Profiling", phase2_profile),
        ("Phase 2b: Synthetic Signature Metrics", phase2b_synthetic_signatures),
        ("Phase 3: Clean & Transform → clean_health", phase3_clean),
        ("Phase 4: Analytical Views", phase4_views),
        ("Phase 4b: Robustness (Dedup-at-Cell Views)", phase4b_robust_views),
        ("Phase 5: Prompt Gap Matrix", phase5_prompt_gap_matrix),
    ]

    total_start = time.time()

    for name, module in phases:
        print(f"\n[START] {name}")
        t0 = time.time()

        module.run(con)
        module.verify(con)

        elapsed = time.time() - t0
        print(f"[DONE]  {name} ({elapsed:.1f}s)")

    total = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"Pipeline complete in {total:.1f}s")

    _write_run_metadata(total_seconds=total)

    # Final table inventory
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name"
    ).fetchall()
    print(f"Tables in {DB_PATH}: {[t[0] for t in tables]}")

    con.close()


if __name__ == "__main__":
    main()
