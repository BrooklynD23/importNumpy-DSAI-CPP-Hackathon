"""Pipeline orchestrator — runs phases 1→2→3→4 with verification gates."""

import time

import duckdb

from pipeline import phase1_ingest, phase2_profile, phase3_clean, phase4_views
from pipeline.config import DB_PATH


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    phases = [
        ("Phase 1: Ingest CSV → raw_health", phase1_ingest),
        ("Phase 2: Data Quality Profiling", phase2_profile),
        ("Phase 3: Clean & Transform → clean_health", phase3_clean),
        ("Phase 4: Analytical Views", phase4_views),
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

    # Final table inventory
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name"
    ).fetchall()
    print(f"Tables in {DB_PATH}: {[t[0] for t in tables]}")

    con.close()


if __name__ == "__main__":
    main()
