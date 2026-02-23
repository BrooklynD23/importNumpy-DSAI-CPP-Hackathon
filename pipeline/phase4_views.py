"""Phase 4: Create 6 analytical views (materialized tables), one per question."""

import duckdb

from pipeline.config import SMALL_N_THRESHOLD


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Create analytical views and indexes."""

    # ── Indexes on clean_health ───────────────────────────────────────────────
    for col in ("country", "disease_category", "urbanization_tier",
                "data_quality_flag"):
        con.execute(
            f"CREATE INDEX IF NOT EXISTS idx_clean_{col} "
            f"ON clean_health ({col})"
        )

    # ── Q1: Outcome disparities by geography ─────────────────────────────────
    con.execute("DROP TABLE IF EXISTS v_outcome_by_geography")
    con.execute(f"""
        CREATE TABLE v_outcome_by_geography AS
        SELECT
            country,
            urbanization_tier,
            disease_category,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            STDDEV_SAMP(mortality_rate) AS sd_mortality,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY mortality_rate) AS q1_mortality,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY mortality_rate) AS median_mortality,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY mortality_rate) AS q3_mortality,
            AVG(recovery_rate) AS avg_recovery,
            STDDEV_SAMP(recovery_rate) AS sd_recovery,
            AVG(dalys) AS avg_dalys,
            STDDEV_SAMP(dalys) AS sd_dalys
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY country, urbanization_tier, disease_category
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    # ── Q2: Access vs outcomes ────────────────────────────────────────────────
    con.execute("DROP TABLE IF EXISTS v_access_vs_outcomes")
    con.execute(f"""
        CREATE TABLE v_access_vs_outcomes AS
        SELECT
            country,
            urbanization_tier,
            age_group,
            COUNT(*) AS n,
            AVG(healthcare_access) AS avg_access,
            AVG(doctors_per_1000) AS avg_doctors,
            AVG(hospital_beds_per_1000) AS avg_beds,
            AVG(access_composite) AS avg_access_composite,
            AVG(mortality_rate) AS avg_mortality,
            AVG(recovery_rate) AS avg_recovery,
            AVG(dalys) AS avg_dalys,
            AVG(access_outcome_gap) AS avg_access_outcome_gap,
            CORR(healthcare_access, mortality_rate) AS corr_access_mortality,
            CORR(healthcare_access, recovery_rate) AS corr_access_recovery
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY country, urbanization_tier, age_group
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    # ── Q3: Outlier communities defying assumptions ──────────────────────────
    con.execute("DROP TABLE IF EXISTS v_outlier_communities")
    con.execute(f"""
        CREATE TABLE v_outlier_communities AS
        WITH country_stats AS (
            SELECT
                country,
                COUNT(*) AS n,
                AVG(healthcare_access) AS avg_access,
                AVG(mortality_rate) AS avg_mortality,
                AVG(recovery_rate) AS avg_recovery,
                AVG(per_capita_income) AS avg_income,
                AVG(education_index) AS avg_education
            FROM clean_health
            WHERE data_quality_flag = 'ok'
            GROUP BY country
            HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
        ),
        global_stats AS (
            SELECT
                AVG(avg_access) AS g_access,
                STDDEV_SAMP(avg_access) AS sd_access,
                AVG(avg_mortality) AS g_mortality,
                STDDEV_SAMP(avg_mortality) AS sd_mortality,
                AVG(avg_recovery) AS g_recovery,
                STDDEV_SAMP(avg_recovery) AS sd_recovery
            FROM country_stats
        )
        SELECT
            cs.*,
            (cs.avg_access - gs.g_access) / NULLIF(gs.sd_access, 0) AS z_access,
            (cs.avg_mortality - gs.g_mortality) / NULLIF(gs.sd_mortality, 0) AS z_mortality,
            (cs.avg_recovery - gs.g_recovery) / NULLIF(gs.sd_recovery, 0) AS z_recovery,
            CASE
                WHEN (cs.avg_access - gs.g_access) / NULLIF(gs.sd_access, 0) > 1
                     AND (cs.avg_mortality - gs.g_mortality) / NULLIF(gs.sd_mortality, 0) > 1
                THEN 'high_access_poor_outcome'
                WHEN (cs.avg_access - gs.g_access) / NULLIF(gs.sd_access, 0) < -1
                     AND (cs.avg_recovery - gs.g_recovery) / NULLIF(gs.sd_recovery, 0) > 1
                THEN 'low_access_good_outcome'
                ELSE 'expected_pattern'
            END AS outlier_type
        FROM country_stats cs
        CROSS JOIN global_stats gs
    """)

    # ── Q4: Sensitivity to geographic tier definitions ────────────────────────
    con.execute("DROP TABLE IF EXISTS v_sensitivity_tiers")
    con.execute(f"""
        CREATE TABLE v_sensitivity_tiers AS
        SELECT
            'default_3tier' AS tier_scheme,
            urbanization_tier AS tier_label,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            AVG(recovery_rate) AS avg_recovery,
            AVG(dalys) AS avg_dalys,
            AVG(healthcare_access) AS avg_access
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY urbanization_tier
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}

        UNION ALL

        SELECT
            'alt1_binary' AS tier_scheme,
            urban_tier_alt1 AS tier_label,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            AVG(recovery_rate) AS avg_recovery,
            AVG(dalys) AS avg_dalys,
            AVG(healthcare_access) AS avg_access
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY urban_tier_alt1
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}

        UNION ALL

        SELECT
            'alt2_4tier' AS tier_scheme,
            urban_tier_alt2 AS tier_label,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            AVG(recovery_rate) AS avg_recovery,
            AVG(dalys) AS avg_dalys,
            AVG(healthcare_access) AS avg_access
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY urban_tier_alt2
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    # ── Q5: Sparse reporting & uncertainty ────────────────────────────────────
    con.execute("DROP TABLE IF EXISTS v_sparse_reporting")
    con.execute(f"""
        CREATE TABLE v_sparse_reporting AS
        SELECT
            country,
            disease_category,
            age_group,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            STDDEV_SAMP(mortality_rate) AS sd_mortality,
            -- CI half-width: t ≈ 1.96 for large N
            1.96 * STDDEV_SAMP(mortality_rate) / NULLIF(SQRT(COUNT(*)), 0)
                AS ci_half_width_mortality,
            AVG(recovery_rate) AS avg_recovery,
            STDDEV_SAMP(recovery_rate) AS sd_recovery,
            1.96 * STDDEV_SAMP(recovery_rate) / NULLIF(SQRT(COUNT(*)), 0)
                AS ci_half_width_recovery,
            CASE
                WHEN COUNT(*) >= {SMALL_N_THRESHOLD} THEN 'adequate'
                WHEN COUNT(*) >= 10 THEN 'marginal'
                ELSE 'insufficient'
            END AS sample_adequacy
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY country, disease_category, age_group
    """)

    # ── Q6: Confounder detection / premature conclusions ─────────────────────
    con.execute("DROP TABLE IF EXISTS v_premature_conclusions")
    con.execute(f"""
        CREATE TABLE v_premature_conclusions AS
        SELECT
            disease_category,
            urbanization_tier,
            COUNT(*) AS n,
            -- Access → Outcome correlations
            CORR(healthcare_access, mortality_rate) AS corr_access_mortality,
            CORR(healthcare_access, recovery_rate) AS corr_access_recovery,
            -- Potential confounders
            CORR(per_capita_income, mortality_rate) AS corr_income_mortality,
            CORR(education_index, mortality_rate) AS corr_education_mortality,
            CORR(per_capita_income, healthcare_access) AS corr_income_access,
            CORR(education_index, healthcare_access) AS corr_education_access,
            -- Confounder flag: if income/education correlate with both
            -- access AND outcome, conclusions about access→outcome may be confounded
            CASE
                WHEN ABS(CORR(per_capita_income, mortality_rate)) > 0.3
                     AND ABS(CORR(per_capita_income, healthcare_access)) > 0.3
                THEN 'income_confounded'
                WHEN ABS(CORR(education_index, mortality_rate)) > 0.3
                     AND ABS(CORR(education_index, healthcare_access)) > 0.3
                THEN 'education_confounded'
                ELSE 'no_strong_confounder'
            END AS confounder_flag
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY disease_category, urbanization_tier
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Verify all 6 analytical views exist and are non-empty."""
    views = [
        "v_outcome_by_geography",
        "v_access_vs_outcomes",
        "v_outlier_communities",
        "v_sensitivity_tiers",
        "v_sparse_reporting",
        "v_premature_conclusions",
    ]
    for view in views:
        count = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
        assert count > 0, f"{view} is empty"
        print(f"  {view}: {count:,} rows")

    # Sensitivity view must have 3 tier schemes
    schemes = con.execute(
        "SELECT COUNT(DISTINCT tier_scheme) FROM v_sensitivity_tiers"
    ).fetchone()[0]
    assert schemes == 3, f"Expected 3 tier schemes, got {schemes}"

    # Outlier view should have some non-expected rows
    outliers = con.execute(
        "SELECT COUNT(*) FROM v_outlier_communities "
        "WHERE outlier_type != 'expected_pattern'"
    ).fetchone()[0]
    print(f"  Outlier communities (non-expected): {outliers}")

    print("  All 6 views verified — OK")
