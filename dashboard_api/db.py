from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import duckdb

from dashboard_api.settings import METRIC_COLUMNS, PATHS


@dataclass(frozen=True)
class Filters:
    year: int | None = None
    disease_category: str | None = None
    disease_name: str | None = None
    age_group: str | None = None
    gender: str | None = None


def connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(PATHS.db_path), read_only=True)


def table_exists(con: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    q = """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'main' AND table_name = ?
    """
    return bool(con.execute(q, [table_name]).fetchone()[0])


def _validate_metric(metric: str) -> str:
    if metric not in METRIC_COLUMNS:
        raise ValueError(f"Unsupported metric: {metric}")
    return metric


def _resolve_source_table(*, dedup: bool) -> str:
    return "cell_health" if dedup else "clean_health"


def _build_where(filters: Filters, *, source_table: str) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    if source_table == "clean_health":
        clauses.append("data_quality_flag = 'ok'")

    if filters.year is not None:
        clauses.append("year = ?")
        params.append(int(filters.year))

    if filters.disease_category:
        clauses.append("disease_category = ?")
        params.append(filters.disease_category)

    if filters.disease_name:
        clauses.append("disease_name = ?")
        params.append(filters.disease_name)

    if filters.age_group:
        clauses.append("age_group = ?")
        params.append(filters.age_group)

    if filters.gender:
        clauses.append("gender = ?")
        params.append(filters.gender)

    if not clauses:
        return "", params

    return " WHERE " + " AND ".join(clauses), params


def get_filter_domains(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    years = [r[0] for r in con.execute("SELECT DISTINCT year FROM clean_health ORDER BY year").fetchall()]
    disease_categories = [
        r[0]
        for r in con.execute(
            "SELECT DISTINCT disease_category FROM clean_health ORDER BY disease_category"
        ).fetchall()
    ]
    disease_names = [
        r[0]
        for r in con.execute(
            "SELECT DISTINCT disease_name FROM clean_health ORDER BY disease_name"
        ).fetchall()
    ]
    age_groups = [
        r[0]
        for r in con.execute(
            "SELECT DISTINCT age_group FROM clean_health ORDER BY age_group"
        ).fetchall()
    ]
    genders = [
        r[0]
        for r in con.execute("SELECT DISTINCT gender FROM clean_health ORDER BY gender").fetchall()
    ]

    return {
        "years": years,
        "disease_categories": disease_categories,
        "disease_names": disease_names,
        "age_groups": age_groups,
        "genders": genders,
        "metrics": list(METRIC_COLUMNS),
        "tables": {
            "clean_health": table_exists(con, "clean_health"),
            "cell_health": table_exists(con, "cell_health"),
            "robustness_delta_summary": table_exists(con, "robustness_delta_summary"),
        },
    }


def get_country_metric(
    con: duckdb.DuckDBPyConnection,
    *,
    metric: str,
    dedup: bool,
    filters: Filters,
) -> list[dict[str, Any]]:
    metric = _validate_metric(metric)
    source_table = _resolve_source_table(dedup=dedup)

    if dedup and not table_exists(con, source_table):
        raise RuntimeError("Dedup source table not found. Run Phase 4b first.")

    where_sql, params = _build_where(filters, source_table=source_table)

    sql = (
        f"SELECT country, AVG({metric}) AS value, COUNT(*) AS n_rows "
        f"FROM {source_table}{where_sql} "
        "GROUP BY country ORDER BY country"
    )
    rows = con.execute(sql, params).fetchall()
    return [{"country": r[0], "value": r[1], "n_rows": int(r[2])} for r in rows]


def get_country_summary(
    con: duckdb.DuckDBPyConnection,
    *,
    country: str,
    dedup: bool,
    filters: Filters,
) -> dict[str, Any]:
    source_table = _resolve_source_table(dedup=dedup)
    if dedup and not table_exists(con, source_table):
        raise RuntimeError("Dedup source table not found. Run Phase 4b first.")

    # Force the selected country
    where_sql, params = _build_where(
        Filters(
            year=filters.year,
            disease_category=filters.disease_category,
            disease_name=filters.disease_name,
            age_group=filters.age_group,
            gender=filters.gender,
        ),
        source_table=source_table,
    )
    if where_sql:
        where_sql += " AND country = ?"
    else:
        where_sql = " WHERE country = ?"
    params.append(country)

    metrics = [
        "mortality_rate",
        "recovery_rate",
        "dalys",
        "healthcare_access",
        "per_capita_income",
        "education_index",
        "urbanization_rate",
    ]

    sql = (
        "SELECT "
        "COUNT(*) AS n_rows, "
        "COUNT(DISTINCT year) AS n_years, "
        "COUNT(DISTINCT disease_name) AS n_diseases, "
        + ", ".join([f"AVG({m}) AS avg_{m}" for m in metrics])
        + f" FROM {source_table}{where_sql}"
    )
    row = con.execute(sql, params).fetchone()
    payload: dict[str, Any] = {
        "country": country,
        "dedup": dedup,
        "n_rows": int(row[0]),
        "n_years": int(row[1]),
        "n_diseases": int(row[2]),
        "averages": {},
    }
    for idx, m in enumerate(metrics, start=3):
        payload["averages"][m] = row[idx]
    return payload


def get_table_counts(con: duckdb.DuckDBPyConnection, table_names: list[str]) -> dict[str, int | None]:
    out: dict[str, int | None] = {}
    for t in table_names:
        if not table_exists(con, t):
            out[t] = None
            continue
        out[t] = int(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
    return out


def get_robustness_summary(con: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    if not table_exists(con, "robustness_delta_summary"):
        return []
    cols = [
        "view_name",
        "base_rows",
        "dedup_rows",
        "base_only_keys",
        "dedup_only_keys",
        "metric1_name",
        "metric1_max_abs_delta",
        "metric2_name",
        "metric2_max_abs_delta",
        "metric3_name",
        "metric3_max_abs_delta",
        "pass",
        "pass_criteria",
    ]
    rows = con.execute(
        "SELECT " + ", ".join(cols) + " FROM robustness_delta_summary ORDER BY view_name"
    ).fetchall()
    out = []
    for r in rows:
        out.append({k: v for k, v in zip(cols, r, strict=True)})
    return out

