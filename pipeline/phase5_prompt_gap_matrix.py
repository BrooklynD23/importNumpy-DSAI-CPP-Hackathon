"""Phase 5: Generate a prompt gap matrix (prompt concepts vs dataset measurements).

This is a judge-defense artifact: it makes explicit where the prompt asks for concepts
that the dataset does not measure (e.g., distance-to-care, utilization) and what proxies
we use instead.

Output:
- reports/prompt_gap_matrix.md
"""

from __future__ import annotations

import duckdb

from pipeline.config import PROJECT_ROOT, REPORTS_DIR


def _render_table(rows: list[dict[str, str]]) -> str:
    headers = [
        "Prompt Question",
        "Required Concept",
        "Measured / Available",
        "Proxy We Use",
        "What We Cannot Claim",
        "Premature Conclusion Risk",
    ]
    md = []
    md.append("| " + " | ".join(headers) + " |")
    md.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        md.append(
            "| "
            + " | ".join(
                [
                    r["prompt_question"],
                    r["required_concept"],
                    r["measured_available"],
                    r["proxy_used"],
                    r["cannot_claim"],
                    r["risk"],
                ]
            )
            + " |"
        )
    return "\n".join(md)


def run(_con: duckdb.DuckDBPyConnection) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    prompt_path = PROJECT_ROOT / "DatathonHostPrompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    rows = [
        {
            "prompt_question": "Q1 — Outcome disparities across geographic classifications",
            "required_concept": "Geography classification differences",
            "measured_available": "country, urbanization_rate, derived tiers; outcomes (mortality/recovery/DALYs)",
            "proxy_used": "urbanization_tier (default + sensitivity tier schemes)",
            "cannot_claim": "Causal statements about geography or rurality causing outcomes",
            "risk": "Large N can make tiny differences look 'significant' — use effect sizes",
        },
        {
            "prompt_question": "Q2 — Distance to care vs utilization/outcomes",
            "required_concept": "Distance + utilization",
            "measured_available": "Access/supply proxies (healthcare_access, doctors, beds), outcomes",
            "proxy_used": "Access proxies only (explicitly label distance/utilization as unmeasured)",
            "cannot_claim": "Any statement specifically about distance-to-care or utilization patterns",
            "risk": "Proxy substitution can mislead unless the measurement gap is explicit",
        },
        {
            "prompt_question": "Q3 — Communities defying access assumptions",
            "required_concept": "Outliers vs expectation",
            "measured_available": "country-level aggregates; access proxies; outcomes",
            "proxy_used": "Z-scores on access vs outcomes; practical-difference checks",
            "cannot_claim": "That an apparent outlier implies a real-world 'exceptional health system'",
            "risk": "Tiny between-group variance inflates z-scores; absolute deltas may be noise-level",
        },
        {
            "prompt_question": "Q4 — Sensitivity to geographic category definitions",
            "required_concept": "Definition dependence",
            "measured_available": "Multiple tier schemes from urbanization_rate",
            "proxy_used": "Compare 3-tier vs binary vs 4-tier schemes",
            "cannot_claim": "Tier definitions matter unless conclusions change meaningfully",
            "risk": "If there is no signal, 'robustness' can be trivial — explain why",
        },
        {
            "prompt_question": "Q5 — Uncertainty from sparse reporting / small populations",
            "required_concept": "Missingness + small-N instability",
            "measured_available": "Group counts; CI half-widths; missingness is ~0 in this dataset",
            "proxy_used": "Observed CI widths + simulated sparsity via subsampling",
            "cannot_claim": "That real-world under-reporting exists here (it is not observed)",
            "risk": "Overinterpreting narrow CIs as 'high certainty' when data structure is synthetic",
        },
        {
            "prompt_question": "Q6 — What conclusions would be premature",
            "required_concept": "Inference limits + confounding",
            "measured_available": "Correlation structure; income/education proxies; entropy checks",
            "proxy_used": "Premature-conclusions framework + expected-vs-observed benchmarks (labeled illustrative)",
            "cannot_claim": "Policy prescriptions from absent structure / near-zero dependence",
            "risk": "Conflating benchmark expectations with observed evidence",
        },
    ]

    out_lines = []
    out_lines.append("# Prompt Gap Matrix")
    out_lines.append("Generated: (see reports/_run_metadata.json)")
    out_lines.append("")
    out_lines.append("This matrix maps the datathon prompt concepts to what the provided dataset actually measures.")
    out_lines.append("It is designed for judge Q&A and to prevent proxy substitution from becoming overclaiming.")
    out_lines.append("")
    if prompt_text:
        out_lines.append("## Prompt Source (repo file)")
        out_lines.append(f"- `{prompt_path.relative_to(PROJECT_ROOT)}`")
        out_lines.append("")
    out_lines.append("## Matrix")
    out_lines.append("")
    out_lines.append(_render_table(rows))
    out_lines.append("")
    out_lines.append("## Notes")
    out_lines.append("- Distance-to-care and utilization are **not measured** in this dataset; we use access proxies only.")
    out_lines.append("- Synthetic/low-signal structure means results are best treated as descriptive of this dataset.")

    out_path = REPORTS_DIR / "prompt_gap_matrix.md"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"  Prompt gap matrix written to {out_path}")


def verify(_con: duckdb.DuckDBPyConnection) -> None:
    out_path = REPORTS_DIR / "prompt_gap_matrix.md"
    assert out_path.exists(), f"Missing {out_path}"
    assert out_path.stat().st_size > 200, "prompt_gap_matrix.md looks too small"
    print("  Prompt gap matrix verified — OK")
