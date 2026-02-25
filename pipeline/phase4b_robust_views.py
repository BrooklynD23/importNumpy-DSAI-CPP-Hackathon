"""Phase 4b: Robustness via dedup-at-cell-grain analytical views.

Motivation
----------
The dataset contains many repeated observations per structural cell. Even if those repeats are
legitimate, they can create the appearance of extremely high confidence (tiny CIs) and over-weight
certain design choices.

Important: Several analyses group by derived geography labels (urbanization tiers). If we dedup
*without* preserving those labels, averaging urbanization_rate inside each cell can collapse the tier
distribution (an artifact of averaging). To keep the robustness check interpretable, we dedup at a
cell grain that **preserves the tier labels used in analysis**.

This phase builds:
- cell_health: aggregated rows per repeated structural cell (means across repeats; preserves tier labels)
- v_*_dedup: mirrors of the Phase 4 analytical tables built from cell_health
- robustness_delta_summary: compact join-based deltas vs the base tables

Notebooks should use robustness_delta_summary for a lightweight "base vs dedup" check without
duplicating full chart logic.
"""

from __future__ import annotations

import duckdb

from pipeline.config import SMALL_N_THRESHOLD


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Create cell_health, dedup analytical views, and robustness delta summary."""

    # ── 1) Dedup-at-cell-grain table (preserving tier labels) ─────────────────
    con.execute("DROP TABLE IF EXISTS cell_health")
    con.execute(f"""
        CREATE TABLE cell_health AS
        SELECT
            country,
            year,
            disease_name,
            disease_category,
            age_group,
            gender,
            urbanization_tier,
            urban_tier_alt1,
            urban_tier_alt2,
            COUNT(*) AS cell_n,
            AVG(prevalence_rate) AS prevalence_rate,
            AVG(incidence_rate) AS incidence_rate,
            AVG(mortality_rate) AS mortality_rate,
            AVG(recovery_rate) AS recovery_rate,
            AVG(dalys) AS dalys,
            AVG(population_affected) AS population_affected,
            AVG(healthcare_access) AS healthcare_access,
            AVG(doctors_per_1000) AS doctors_per_1000,
            AVG(hospital_beds_per_1000) AS hospital_beds_per_1000,
            AVG(avg_treatment_cost_usd) AS avg_treatment_cost_usd,
            AVG(improvement_in_5_years) AS improvement_in_5_years,
            AVG(per_capita_income) AS per_capita_income,
            AVG(education_index) AS education_index,
            AVG(urbanization_rate) AS urbanization_rate,
            AVG(resource_index) AS resource_index,
            AVG(access_outcome_gap) AS access_outcome_gap,
            AVG(access_composite) AS access_composite,
            AVG(cost_burden_ratio) AS cost_burden_ratio
        FROM clean_health
        WHERE data_quality_flag = 'ok'
        GROUP BY
            country,
            year,
            disease_name,
            disease_category,
            age_group,
            gender,
            urbanization_tier,
            urban_tier_alt1,
            urban_tier_alt2
    """)

    for col in ("country", "disease_category", "urbanization_tier"):
        con.execute(
            f"CREATE INDEX IF NOT EXISTS idx_cell_{col} ON cell_health ({col})"
        )

    # ── 2) Dedup analytical tables (mirrors of Phase 4) ───────────────────────
    con.execute("DROP TABLE IF EXISTS v_outcome_by_geography_dedup")
    con.execute(f"""
        CREATE TABLE v_outcome_by_geography_dedup AS
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
        FROM cell_health
        GROUP BY country, urbanization_tier, disease_category
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    con.execute("DROP TABLE IF EXISTS v_access_vs_outcomes_dedup")
    con.execute(f"""
        CREATE TABLE v_access_vs_outcomes_dedup AS
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
        FROM cell_health
        GROUP BY country, urbanization_tier, age_group
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    con.execute("DROP TABLE IF EXISTS v_outlier_communities_dedup")
    con.execute(f"""
        CREATE TABLE v_outlier_communities_dedup AS
        WITH country_stats AS (
            SELECT
                country,
                COUNT(*) AS n,
                AVG(healthcare_access) AS avg_access,
                AVG(mortality_rate) AS avg_mortality,
                AVG(recovery_rate) AS avg_recovery,
                AVG(per_capita_income) AS avg_income,
                AVG(education_index) AS avg_education
            FROM cell_health
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

    con.execute("DROP TABLE IF EXISTS v_sensitivity_tiers_dedup")
    con.execute(f"""
        CREATE TABLE v_sensitivity_tiers_dedup AS
        SELECT
            'default_3tier' AS tier_scheme,
            urbanization_tier AS tier_label,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            AVG(recovery_rate) AS avg_recovery,
            AVG(dalys) AS avg_dalys,
            AVG(healthcare_access) AS avg_access
        FROM cell_health
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
        FROM cell_health
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
        FROM cell_health
        GROUP BY urban_tier_alt2
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    con.execute("DROP TABLE IF EXISTS v_sparse_reporting_dedup")
    con.execute(f"""
        CREATE TABLE v_sparse_reporting_dedup AS
        SELECT
            country,
            disease_category,
            age_group,
            COUNT(*) AS n,
            AVG(mortality_rate) AS avg_mortality,
            STDDEV_SAMP(mortality_rate) AS sd_mortality,
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
        FROM cell_health
        GROUP BY country, disease_category, age_group
    """)

    con.execute("DROP TABLE IF EXISTS v_premature_conclusions_dedup")
    con.execute(f"""
        CREATE TABLE v_premature_conclusions_dedup AS
        SELECT
            disease_category,
            urbanization_tier,
            COUNT(*) AS n,
            CORR(healthcare_access, mortality_rate) AS corr_access_mortality,
            CORR(healthcare_access, recovery_rate) AS corr_access_recovery,
            CORR(per_capita_income, mortality_rate) AS corr_income_mortality,
            CORR(education_index, mortality_rate) AS corr_education_mortality,
            CORR(per_capita_income, healthcare_access) AS corr_income_access,
            CORR(education_index, healthcare_access) AS corr_education_access,
            CASE
                WHEN ABS(CORR(per_capita_income, mortality_rate)) > 0.3
                     AND ABS(CORR(per_capita_income, healthcare_access)) > 0.3
                THEN 'income_confounded'
                WHEN ABS(CORR(education_index, mortality_rate)) > 0.3
                     AND ABS(CORR(education_index, healthcare_access)) > 0.3
                THEN 'education_confounded'
                ELSE 'no_strong_confounder'
            END AS confounder_flag
        FROM cell_health
        GROUP BY disease_category, urbanization_tier
        HAVING COUNT(*) >= {SMALL_N_THRESHOLD}
    """)

    # ── 3) Compact delta summary for notebooks / executive report ─────────────
    con.execute("DROP TABLE IF EXISTS robustness_delta_summary")
    con.execute(f"""
        CREATE TABLE robustness_delta_summary AS

        -- Q1 deltas
        WITH j AS (
            SELECT
                b.country AS b_country,
                d.country AS d_country,
                b.avg_mortality AS b_avg_mortality,
                d.avg_mortality AS d_avg_mortality,
                b.avg_recovery AS b_avg_recovery,
                d.avg_recovery AS d_avg_recovery,
                b.avg_dalys AS b_avg_dalys,
                d.avg_dalys AS d_avg_dalys
            FROM v_outcome_by_geography b
            FULL OUTER JOIN v_outcome_by_geography_dedup d
              ON b.country = d.country
             AND b.urbanization_tier = d.urbanization_tier
             AND b.disease_category = d.disease_category
        ),
        q1 AS (
            SELECT
                'v_outcome_by_geography' AS view_name,
                (SELECT COUNT(*) FROM v_outcome_by_geography) AS base_rows,
                (SELECT COUNT(*) FROM v_outcome_by_geography_dedup) AS dedup_rows,
                SUM(CASE WHEN b_country IS NOT NULL AND d_country IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_country IS NOT NULL AND b_country IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'avg_mortality' AS metric1_name,
                MAX(ABS(b_avg_mortality - d_avg_mortality)) AS metric1_max_abs_delta,
                'avg_recovery' AS metric2_name,
                MAX(ABS(b_avg_recovery - d_avg_recovery)) AS metric2_max_abs_delta,
                'avg_dalys' AS metric3_name,
                MAX(ABS(b_avg_dalys - d_avg_dalys)) AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_avg_mortality - d_avg_mortality)) < 0.25
                     AND MAX(ABS(b_avg_recovery - d_avg_recovery)) < 1.00
                     AND MAX(ABS(b_avg_dalys - d_avg_dalys)) < 100.0
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: mortality<0.25pp, recovery<1.00pp, DALYs<100' AS pass_criteria
            FROM j
        ),

        -- Q2 deltas
        j2 AS (
            SELECT
                b.country AS b_country,
                d.country AS d_country,
                b.avg_access AS b_avg_access,
                d.avg_access AS d_avg_access,
                b.avg_mortality AS b_avg_mortality,
                d.avg_mortality AS d_avg_mortality,
                b.corr_access_mortality AS b_corr,
                d.corr_access_mortality AS d_corr
            FROM v_access_vs_outcomes b
            FULL OUTER JOIN v_access_vs_outcomes_dedup d
              ON b.country = d.country
             AND b.urbanization_tier = d.urbanization_tier
             AND b.age_group = d.age_group
        ),
        q2 AS (
            SELECT
                'v_access_vs_outcomes' AS view_name,
                (SELECT COUNT(*) FROM v_access_vs_outcomes) AS base_rows,
                (SELECT COUNT(*) FROM v_access_vs_outcomes_dedup) AS dedup_rows,
                SUM(CASE WHEN b_country IS NOT NULL AND d_country IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_country IS NOT NULL AND b_country IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'avg_access' AS metric1_name,
                MAX(ABS(b_avg_access - d_avg_access)) AS metric1_max_abs_delta,
                'avg_mortality' AS metric2_name,
                MAX(ABS(b_avg_mortality - d_avg_mortality)) AS metric2_max_abs_delta,
                'corr_access_mortality' AS metric3_name,
                MAX(ABS(b_corr - d_corr)) AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_avg_access - d_avg_access)) < 1.0
                     AND MAX(ABS(b_avg_mortality - d_avg_mortality)) < 0.25
                     AND MAX(ABS(b_corr - d_corr)) < 0.10
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: access<1.0pp, mortality<0.25pp, corr<0.10' AS pass_criteria
            FROM j2
        ),

        -- Q3 deltas (includes outlier_type mismatch rate)
        j3 AS (
            SELECT
                b.country AS b_country,
                d.country AS d_country,
                b.avg_access AS b_avg_access,
                d.avg_access AS d_avg_access,
                b.avg_mortality AS b_avg_mortality,
                d.avg_mortality AS d_avg_mortality,
                b.outlier_type AS b_outlier_type,
                d.outlier_type AS d_outlier_type
            FROM v_outlier_communities b
            FULL OUTER JOIN v_outlier_communities_dedup d
              ON b.country = d.country
        ),
        q3 AS (
            SELECT
                'v_outlier_communities' AS view_name,
                (SELECT COUNT(*) FROM v_outlier_communities) AS base_rows,
                (SELECT COUNT(*) FROM v_outlier_communities_dedup) AS dedup_rows,
                SUM(CASE WHEN b_country IS NOT NULL AND d_country IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_country IS NOT NULL AND b_country IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'avg_access' AS metric1_name,
                MAX(ABS(b_avg_access - d_avg_access)) AS metric1_max_abs_delta,
                'avg_mortality' AS metric2_name,
                MAX(ABS(b_avg_mortality - d_avg_mortality)) AS metric2_max_abs_delta,
                'outlier_type_mismatch_rate' AS metric3_name,
                AVG(
                    CASE
                        WHEN b_country IS NOT NULL AND d_country IS NOT NULL
                             AND b_outlier_type != d_outlier_type
                        THEN 1.0 ELSE 0.0
                    END
                ) AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_avg_access - d_avg_access)) < 0.5
                     AND MAX(ABS(b_avg_mortality - d_avg_mortality)) < 0.05
                     AND AVG(
                        CASE
                            WHEN b_country IS NOT NULL AND d_country IS NOT NULL
                                 AND b_outlier_type != d_outlier_type
                            THEN 1.0 ELSE 0.0
                        END
                     ) < 0.05
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: access<0.5pp, mortality<0.05pp, mismatch<5%' AS pass_criteria
            FROM j3
        ),

        -- Q4 deltas
        j4 AS (
            SELECT
                b.tier_scheme AS b_scheme,
                d.tier_scheme AS d_scheme,
                b.avg_mortality AS b_avg_mortality,
                d.avg_mortality AS d_avg_mortality,
                b.avg_access AS b_avg_access,
                d.avg_access AS d_avg_access,
                b.avg_dalys AS b_avg_dalys,
                d.avg_dalys AS d_avg_dalys
            FROM v_sensitivity_tiers b
            FULL OUTER JOIN v_sensitivity_tiers_dedup d
              ON b.tier_scheme = d.tier_scheme
             AND b.tier_label = d.tier_label
        ),
        q4 AS (
            SELECT
                'v_sensitivity_tiers' AS view_name,
                (SELECT COUNT(*) FROM v_sensitivity_tiers) AS base_rows,
                (SELECT COUNT(*) FROM v_sensitivity_tiers_dedup) AS dedup_rows,
                SUM(CASE WHEN b_scheme IS NOT NULL AND d_scheme IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_scheme IS NOT NULL AND b_scheme IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'avg_mortality' AS metric1_name,
                MAX(ABS(b_avg_mortality - d_avg_mortality)) AS metric1_max_abs_delta,
                'avg_access' AS metric2_name,
                MAX(ABS(b_avg_access - d_avg_access)) AS metric2_max_abs_delta,
                'avg_dalys' AS metric3_name,
                MAX(ABS(b_avg_dalys - d_avg_dalys)) AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_avg_mortality - d_avg_mortality)) < 0.05
                     AND MAX(ABS(b_avg_access - d_avg_access)) < 0.5
                     AND MAX(ABS(b_avg_dalys - d_avg_dalys)) < 10.0
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: mortality<0.05pp, access<0.5pp, DALYs<10' AS pass_criteria
            FROM j4
        ),

        -- Q5 deltas
        j5 AS (
            SELECT
                b.country AS b_country,
                d.country AS d_country,
                b.avg_mortality AS b_avg_mortality,
                d.avg_mortality AS d_avg_mortality,
                b.ci_half_width_mortality AS b_ci,
                d.ci_half_width_mortality AS d_ci
            FROM v_sparse_reporting b
            FULL OUTER JOIN v_sparse_reporting_dedup d
              ON b.country = d.country
             AND b.disease_category = d.disease_category
             AND b.age_group = d.age_group
        ),
        q5 AS (
            SELECT
                'v_sparse_reporting' AS view_name,
                (SELECT COUNT(*) FROM v_sparse_reporting) AS base_rows,
                (SELECT COUNT(*) FROM v_sparse_reporting_dedup) AS dedup_rows,
                SUM(CASE WHEN b_country IS NOT NULL AND d_country IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_country IS NOT NULL AND b_country IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'avg_mortality' AS metric1_name,
                MAX(ABS(b_avg_mortality - d_avg_mortality)) AS metric1_max_abs_delta,
                'ci_half_width_mortality' AS metric2_name,
                MAX(ABS(b_ci - d_ci)) AS metric2_max_abs_delta,
                'n/a' AS metric3_name,
                NULL AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_avg_mortality - d_avg_mortality)) < 0.25
                     AND MAX(ABS(b_ci - d_ci)) < 0.10
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: mortality<0.25pp, CI_half_width<0.10' AS pass_criteria
            FROM j5
        ),

        -- Q6 deltas
        j6 AS (
            SELECT
                b.disease_category AS b_cat,
                d.disease_category AS d_cat,
                b.corr_access_mortality AS b_cam,
                d.corr_access_mortality AS d_cam,
                b.corr_income_access AS b_cia,
                d.corr_income_access AS d_cia,
                b.corr_income_mortality AS b_cim,
                d.corr_income_mortality AS d_cim
            FROM v_premature_conclusions b
            FULL OUTER JOIN v_premature_conclusions_dedup d
              ON b.disease_category = d.disease_category
             AND b.urbanization_tier = d.urbanization_tier
        ),
        q6 AS (
            SELECT
                'v_premature_conclusions' AS view_name,
                (SELECT COUNT(*) FROM v_premature_conclusions) AS base_rows,
                (SELECT COUNT(*) FROM v_premature_conclusions_dedup) AS dedup_rows,
                SUM(CASE WHEN b_cat IS NOT NULL AND d_cat IS NULL THEN 1 ELSE 0 END) AS base_only_keys,
                SUM(CASE WHEN d_cat IS NOT NULL AND b_cat IS NULL THEN 1 ELSE 0 END) AS dedup_only_keys,
                'corr_access_mortality' AS metric1_name,
                MAX(ABS(b_cam - d_cam)) AS metric1_max_abs_delta,
                'corr_income_access' AS metric2_name,
                MAX(ABS(b_cia - d_cia)) AS metric2_max_abs_delta,
                'corr_income_mortality' AS metric3_name,
                MAX(ABS(b_cim - d_cim)) AS metric3_max_abs_delta,
                CASE
                    WHEN MAX(ABS(b_cam - d_cam)) < 0.02
                     AND MAX(ABS(b_cia - d_cia)) < 0.02
                     AND MAX(ABS(b_cim - d_cim)) < 0.02
                    THEN TRUE ELSE FALSE
                END AS pass,
                'Thresholds: correlation deltas < 0.02' AS pass_criteria
            FROM j6
        )

        SELECT * FROM q1
        UNION ALL SELECT * FROM q2
        UNION ALL SELECT * FROM q3
        UNION ALL SELECT * FROM q4
        UNION ALL SELECT * FROM q5
        UNION ALL SELECT * FROM q6
    """)


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Verify dedup tables exist and are non-empty."""
    tables = [
        "cell_health",
        "v_outcome_by_geography_dedup",
        "v_access_vs_outcomes_dedup",
        "v_outlier_communities_dedup",
        "v_sensitivity_tiers_dedup",
        "v_sparse_reporting_dedup",
        "v_premature_conclusions_dedup",
        "robustness_delta_summary",
    ]
    for t in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert count > 0, f"{t} is empty"
        print(f"  {t}: {count:,} rows")

    # Ensure we still have 3 tier schemes in the dedup sensitivity table
    schemes = con.execute(
        "SELECT COUNT(DISTINCT tier_scheme) FROM v_sensitivity_tiers_dedup"
    ).fetchone()[0]
    assert schemes == 3, f"Expected 3 tier schemes in dedup view, got {schemes}"

    print("  Robustness (dedup) views verified — OK")
