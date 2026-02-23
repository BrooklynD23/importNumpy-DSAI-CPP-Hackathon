"""Phase 1: Ingest CSV into DuckDB raw_health table."""

import duckdb

from pipeline.config import DB_PATH, RAW_CSV


def run(con: duckdb.DuckDBPyConnection) -> None:
    """Load CSV into raw_health with snake_case columns and computed fields."""

    csv_path = str(RAW_CSV)

    # Drop if re-running
    con.execute("DROP TABLE IF EXISTS raw_health")

    # Create raw_health with explicit column renames and types
    con.execute(f"""
        CREATE TABLE raw_health AS
        SELECT
            ROW_NUMBER() OVER () AS row_id,
            "Country"                           AS country,
            CAST("Year" AS INTEGER)             AS year,
            "Disease Name"                      AS disease_name,
            "Disease Category"                  AS disease_category_original,
            CAST("Prevalence Rate (%)" AS DOUBLE)       AS prevalence_rate,
            CAST("Incidence Rate (%)" AS DOUBLE)        AS incidence_rate,
            CAST("Mortality Rate (%)" AS DOUBLE)        AS mortality_rate,
            "Age Group"                         AS age_group,
            "Gender"                            AS gender,
            CAST("Population Affected" AS BIGINT)       AS population_affected,
            CAST("Healthcare Access (%)" AS DOUBLE)     AS healthcare_access,
            CAST("Doctors per 1000" AS DOUBLE)          AS doctors_per_1000,
            CAST("Hospital Beds per 1000" AS DOUBLE)    AS hospital_beds_per_1000,
            "Treatment Type"                    AS treatment_type,
            CAST("Average Treatment Cost (USD)" AS DOUBLE) AS avg_treatment_cost_usd,
            CAST("Availability of Vaccines/Treatment" AS VARCHAR) AS vaccine_treatment_available,
            CAST("Recovery Rate (%)" AS DOUBLE)         AS recovery_rate,
            CAST("DALYs" AS DOUBLE)                     AS dalys,
            CAST("Improvement in 5 Years (%)" AS DOUBLE) AS improvement_in_5_years,
            CAST("Per Capita Income (USD)" AS DOUBLE)   AS per_capita_income,
            CAST("Education Index" AS DOUBLE)           AS education_index,
            CAST("Urbanization Rate (%)" AS DOUBLE)     AS urbanization_rate
        FROM read_csv_auto('{csv_path}')
    """)

    # Add computed columns
    con.execute("""
        ALTER TABLE raw_health ADD COLUMN urbanization_tier VARCHAR
    """)
    con.execute("""
        UPDATE raw_health SET urbanization_tier = CASE
            WHEN urbanization_rate < 30 THEN 'Rural'
            WHEN urbanization_rate < 70 THEN 'Peri-urban'
            ELSE 'Urban'
        END
    """)

    con.execute("""
        ALTER TABLE raw_health ADD COLUMN resource_index DOUBLE
    """)
    con.execute("""
        UPDATE raw_health SET resource_index =
            (doctors_per_1000 / 5.0 + hospital_beds_per_1000 / 10.0) / 2.0
    """)


def verify(con: duckdb.DuckDBPyConnection) -> None:
    """Run verification checks on raw_health."""
    row_count = con.execute("SELECT COUNT(*) FROM raw_health").fetchone()[0]
    assert row_count == 1_000_000, f"Expected 1M rows, got {row_count}"

    col_count = con.execute(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_name = 'raw_health'"
    ).fetchone()[0]
    assert col_count == 25, f"Expected 25 columns, got {col_count}"

    null_ids = con.execute(
        "SELECT COUNT(*) FROM raw_health WHERE row_id IS NULL"
    ).fetchone()[0]
    assert null_ids == 0, f"Found {null_ids} NULL row_ids"

    tiers = con.execute(
        "SELECT COUNT(DISTINCT urbanization_tier) FROM raw_health"
    ).fetchone()[0]
    assert tiers == 3, f"Expected 3 urbanization tiers, got {tiers}"

    print(f"  raw_health: {row_count:,} rows, {col_count} columns, "
          f"{tiers} tiers — OK")
