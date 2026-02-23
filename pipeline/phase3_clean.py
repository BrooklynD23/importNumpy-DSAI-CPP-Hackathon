"""Phase 3: Clean and transform raw_health → clean_health + country_summary."""

import duckdb

from pipeline.config import DISEASE_CATEGORY_MAP, SMALL_N_THRESHOLD


def _build_disease_case_sql() -> str:
    """Build a SQL CASE expression from the disease category map."""
    whens = "\n            ".join(
        f"WHEN disease_name = '{name.replace(chr(39), chr(39)+chr(39))}' THEN '{cat}'"
        for name, cat in DISEASE_CATEGORY_MAP.items()
    )
    return f"""CASE
            {whens}
            ELSE 'Unmapped'
        END"""


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Create clean_health and country_summary tables."""

    disease_case = _build_disease_case_sql()

    con.execute("DROP TABLE IF EXISTS clean_health")
    con.execute(f"""
        CREATE TABLE clean_health AS
        SELECT
            row_id,
            country,
            year,
            disease_name,
            disease_category_original,
            {disease_case} AS disease_category,
            prevalence_rate,
            incidence_rate,
            mortality_rate,
            TRIM(age_group) AS age_group,
            TRIM(gender) AS gender,
            population_affected,
            healthcare_access,
            doctors_per_1000,
            hospital_beds_per_1000,
            TRIM(treatment_type) AS treatment_type,
            avg_treatment_cost_usd,
            UPPER(TRIM(CAST(vaccine_treatment_available AS VARCHAR))) AS vaccine_treatment_available,
            recovery_rate,
            dalys,
            improvement_in_5_years,
            per_capita_income,
            education_index,
            urbanization_rate,
            urbanization_tier,
            resource_index,

            -- access_outcome_gap: positive = access exceeds recovery
            healthcare_access - recovery_rate AS access_outcome_gap,

            -- access_composite: weighted score (0-1 scale)
            0.5 * (healthcare_access / 100.0)
                + 0.25 * (doctors_per_1000 / 5.0)
                + 0.25 * (hospital_beds_per_1000 / 10.0)
            AS access_composite,

            -- cost_burden_ratio: treatment cost as fraction of income
            CASE
                WHEN per_capita_income > 0
                THEN avg_treatment_cost_usd / per_capita_income
                ELSE NULL
            END AS cost_burden_ratio,

            -- data_quality_flag
            CASE
                WHEN prevalence_rate < 0 OR prevalence_rate > 100
                     OR incidence_rate < 0 OR incidence_rate > 100
                     OR mortality_rate < 0 OR mortality_rate > 100
                     OR recovery_rate < 0 OR recovery_rate > 100
                     OR healthcare_access < 0 OR healthcare_access > 100
                     OR urbanization_rate < 0 OR urbanization_rate > 100
                THEN 'outlier_rate'
                WHEN avg_treatment_cost_usd < 0 OR per_capita_income < 0
                THEN 'negative_cost'
                WHEN {disease_case} = 'Unmapped'
                THEN 'unmapped_disease'
                ELSE 'ok'
            END AS data_quality_flag,

            -- Alternative urbanization tiers for sensitivity (Question 4)
            CASE
                WHEN urbanization_rate < 40 THEN 'Rural'
                ELSE 'Urban'
            END AS urban_tier_alt1,

            CASE
                WHEN urbanization_rate < 25 THEN 'Rural'
                WHEN urbanization_rate < 50 THEN 'Peri-urban'
                WHEN urbanization_rate < 75 THEN 'Semi-urban'
                ELSE 'Urban'
            END AS urban_tier_alt2

        FROM raw_health
    """)

    # ── Country Summary ───────────────────────────────────────────────────────
    con.execute("DROP TABLE IF EXISTS country_summary")
    con.execute(f"""
        CREATE TABLE country_summary AS
        SELECT
            country,
            COUNT(*) AS observation_count,
            COUNT(DISTINCT disease_name) AS disease_count,
            COUNT(DISTINCT year) AS year_span,
            AVG(mortality_rate) AS avg_mortality_rate,
            AVG(recovery_rate) AS avg_recovery_rate,
            AVG(healthcare_access) AS avg_healthcare_access,
            AVG(doctors_per_1000) AS avg_doctors_per_1000,
            AVG(hospital_beds_per_1000) AS avg_hospital_beds_per_1000,
            AVG(per_capita_income) AS avg_per_capita_income,
            AVG(education_index) AS avg_education_index,
            AVG(urbanization_rate) AS avg_urbanization_rate,
            SUM(CASE WHEN data_quality_flag != 'ok' THEN 1 ELSE 0 END)
                AS flagged_rows,
            CASE
                WHEN COUNT(*) < {SMALL_N_THRESHOLD} THEN TRUE
                ELSE FALSE
            END AS small_n_flag
        FROM clean_health
        GROUP BY country
    """)


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Verify clean_health and country_summary."""
    raw_count = con.execute("SELECT COUNT(*) FROM raw_health").fetchone()[0]
    clean_count = con.execute("SELECT COUNT(*) FROM clean_health").fetchone()[0]
    assert clean_count == raw_count, (
        f"Row count mismatch: raw={raw_count}, clean={clean_count}"
    )

    null_cats = con.execute(
        "SELECT COUNT(*) FROM clean_health WHERE disease_category IS NULL"
    ).fetchone()[0]
    assert null_cats == 0, f"Found {null_cats} NULL disease_category values"

    unmapped = con.execute(
        "SELECT COUNT(*) FROM clean_health WHERE disease_category = 'Unmapped'"
    ).fetchone()[0]
    assert unmapped == 0, f"Found {unmapped} unmapped disease categories"

    # Check quality flag distribution
    flags = con.execute("""
        SELECT data_quality_flag, COUNT(*) AS n
        FROM clean_health
        GROUP BY data_quality_flag
        ORDER BY n DESC
    """).fetchall()
    ok_count = next((r[1] for r in flags if r[0] == "ok"), 0)
    ok_pct = ok_count / clean_count
    print(f"  clean_health: {clean_count:,} rows, "
          f"quality flags: {dict(flags)}, ok={ok_pct:.1%}")
    assert ok_pct > 0.5, f"Less than 50% ok rows ({ok_pct:.1%})"

    # Country summary: one row per country
    countries_raw = con.execute(
        "SELECT COUNT(DISTINCT country) FROM raw_health"
    ).fetchone()[0]
    countries_summary = con.execute(
        "SELECT COUNT(*) FROM country_summary"
    ).fetchone()[0]
    assert countries_summary == countries_raw, (
        f"country_summary has {countries_summary} rows, "
        f"expected {countries_raw} distinct countries"
    )
    print(f"  country_summary: {countries_summary} countries — OK")
