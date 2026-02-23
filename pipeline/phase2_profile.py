"""Phase 2: Data quality profiling — read-only on raw_health, writes reports."""

import csv
from datetime import datetime, timezone

import duckdb

from pipeline.config import (
    DISEASE_CATEGORY_MAP,
    MISSINGNESS_FLAG_THRESHOLD,
    RATE_COLUMNS,
    REPORTS_DIR,
    SMALL_N_THRESHOLD,
)


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Generate data quality report and assumption log."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_lines: list[str] = []
    assumptions: list[dict[str, str]] = []

    def _h(text: str) -> None:
        report_lines.append(f"\n## {text}\n")

    def _p(text: str) -> None:
        report_lines.append(text)

    report_lines.append("# Data Quality Report")
    report_lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")

    # ── 1. Missingness ────────────────────────────────────────────────────────
    _h("Missingness by Column")
    total_rows = con.execute("SELECT COUNT(*) FROM raw_health").fetchone()[0]
    cols = [
        r[0]
        for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'raw_health' ORDER BY ordinal_position"
        ).fetchall()
    ]
    _p("| Column | NULLs | % | Flagged |")
    _p("|--------|-------|---|---------|")
    for col in cols:
        null_count = con.execute(
            f'SELECT COUNT(*) FROM raw_health WHERE "{col}" IS NULL'
        ).fetchone()[0]
        pct = null_count / total_rows
        flag = "YES" if pct > MISSINGNESS_FLAG_THRESHOLD else ""
        _p(f"| {col} | {null_count:,} | {pct:.4%} | {flag} |")
    assumptions.append({
        "id": "A1",
        "assumption": f"Columns with >{MISSINGNESS_FLAG_THRESHOLD:.0%} NULLs flagged for review",
        "impact": "May bias aggregate statistics",
        "mitigation": "Filter or impute in Phase 3",
    })

    # ── 2. Outliers on rate columns ───────────────────────────────────────────
    _h("Rate Column Ranges (expected 0–100)")
    _p("| Column | Min | Max | Out-of-range Count |")
    _p("|--------|-----|-----|--------------------|")
    for col in RATE_COLUMNS:
        stats = con.execute(
            f"SELECT MIN({col}), MAX({col}), "
            f"SUM(CASE WHEN {col} < 0 OR {col} > 100 THEN 1 ELSE 0 END) "
            f"FROM raw_health"
        ).fetchone()
        _p(f"| {col} | {stats[0]:.2f} | {stats[1]:.2f} | {stats[2]:,} |")

    _h("Cost and Income Ranges")
    for col in ("avg_treatment_cost_usd", "per_capita_income"):
        stats = con.execute(
            f"SELECT MIN({col}), MAX({col}), "
            f"SUM(CASE WHEN {col} < 0 THEN 1 ELSE 0 END) "
            f"FROM raw_health"
        ).fetchone()
        _p(f"- **{col}**: min={stats[0]:.2f}, max={stats[1]:.2f}, "
           f"negative={stats[2]:,}")

    assumptions.append({
        "id": "A2",
        "assumption": "Rate columns should be in [0, 100]; cost/income should be > 0",
        "impact": "Out-of-range values flagged in data_quality_flag",
        "mitigation": "Flagged rows excluded from analytical views",
    })

    # ── 3. Duplicates ─────────────────────────────────────────────────────────
    _h("Duplicate Check")
    dup_count = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT country, year, disease_name, age_group, gender,
                   COUNT(*) AS n
            FROM raw_health
            GROUP BY country, year, disease_name, age_group, gender
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    _p(f"Duplicate groups (country × year × disease × age × gender): "
       f"**{dup_count:,}**")
    assumptions.append({
        "id": "A3",
        "assumption": "Duplicates are legitimate repeated observations, not data errors",
        "impact": "Aggregations use all rows",
        "mitigation": "Sensitivity analysis could deduplicate",
    })

    # ── 4. Disease Category Audit ─────────────────────────────────────────────
    _h("Disease Category Reliability Audit")
    cat_audit = con.execute("""
        SELECT disease_name,
               COUNT(DISTINCT disease_category_original) AS n_cats,
               LIST(DISTINCT disease_category_original) AS cats
        FROM raw_health
        GROUP BY disease_name
        ORDER BY n_cats DESC
    """).fetchall()
    _p("| Disease | # Original Categories | Categories |")
    _p("|---------|----------------------|------------|")
    for row in cat_audit:
        _p(f"| {row[0]} | {row[1]} | {row[2]} |")
    assumptions.append({
        "id": "A4",
        "assumption": "Original Disease Category column is unreliable — replaced by hand-curated map",
        "impact": "All category-based analyses use corrected mapping",
        "mitigation": "disease_category_original kept for audit trail",
    })

    # ── 5. Small-N Countries ──────────────────────────────────────────────────
    _h("Small-N Countries (< 30 observations)")
    small_n = con.execute(f"""
        SELECT country, COUNT(*) AS n
        FROM raw_health
        GROUP BY country
        HAVING COUNT(*) < {SMALL_N_THRESHOLD}
        ORDER BY n
    """).fetchall()
    if small_n:
        _p("| Country | Observations |")
        _p("|---------|-------------|")
        for row in small_n:
            _p(f"| {row[0]} | {row[1]} |")
    else:
        _p(f"No countries with fewer than {SMALL_N_THRESHOLD} observations.")
    assumptions.append({
        "id": "A5",
        "assumption": f"Countries with <{SMALL_N_THRESHOLD} observations flagged as small-N",
        "impact": "Unstable estimates; wider confidence intervals",
        "mitigation": "small_n_flag in country_summary; minimum N enforced in views",
    })

    # ── 6. Distinct Value Inventory ───────────────────────────────────────────
    _h("Distinct Value Inventory")
    for col in ("disease_name", "age_group", "gender", "treatment_type",
                "vaccine_treatment_available"):
        vals = con.execute(
            f"SELECT DISTINCT {col} FROM raw_health ORDER BY {col}"
        ).fetchall()
        _p(f"- **{col}** ({len(vals)}): {', '.join(str(v[0]) for v in vals)}")

    # ── 7. Unmapped Diseases Check ────────────────────────────────────────────
    _h("Unmapped Disease Names")
    all_diseases = {
        r[0]
        for r in con.execute(
            "SELECT DISTINCT disease_name FROM raw_health"
        ).fetchall()
    }
    unmapped = all_diseases - set(DISEASE_CATEGORY_MAP.keys())
    if unmapped:
        _p(f"**WARNING — unmapped diseases:** {', '.join(sorted(unmapped))}")
        _p("These must be added to DISEASE_CATEGORY_MAP before Phase 3.")
    else:
        _p("All disease names covered by DISEASE_CATEGORY_MAP.")

    # ── Write Reports ─────────────────────────────────────────────────────────
    report_path = REPORTS_DIR / "data_quality_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"  Report written to {report_path}")

    assumption_path = REPORTS_DIR / "assumption_log.csv"
    with assumption_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "assumption", "impact", "mitigation"])
        writer.writeheader()
        writer.writerows(assumptions)
    print(f"  Assumption log written to {assumption_path} ({len(assumptions)} entries)")


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Verify reports were generated."""
    report_path = REPORTS_DIR / "data_quality_report.md"
    assert report_path.exists(), f"Missing {report_path}"
    assert report_path.stat().st_size > 0, "Report is empty"

    assumption_path = REPORTS_DIR / "assumption_log.csv"
    assert assumption_path.exists(), f"Missing {assumption_path}"
    with assumption_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 5, f"Expected ≥5 assumptions, got {len(rows)}"

    # Verify all diseases are mapped
    all_diseases = {
        r[0]
        for r in con.execute(
            "SELECT DISTINCT disease_name FROM raw_health"
        ).fetchall()
    }
    unmapped = all_diseases - set(DISEASE_CATEGORY_MAP.keys())
    assert not unmapped, (
        f"Unmapped diseases found: {unmapped}. "
        "Update DISEASE_CATEGORY_MAP in config.py before proceeding."
    )

    print(f"  Reports verified — OK")
