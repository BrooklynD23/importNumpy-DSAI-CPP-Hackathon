# Prompt Gap Matrix
Generated: (see reports/_run_metadata.json)

This matrix maps the datathon prompt concepts to what the provided dataset actually measures.
It is designed for judge Q&A and to prevent proxy substitution from becoming overclaiming.

## Prompt Source (repo file)
- `DatathonHostPrompt.md`

## Matrix

| Prompt Question | Required Concept | Measured / Available | Proxy We Use | What We Cannot Claim | Premature Conclusion Risk |
|---|---|---|---|---|---|
| Q1 — Outcome disparities across geographic classifications | Geography classification differences | country, urbanization_rate, derived tiers; outcomes (mortality/recovery/DALYs) | urbanization_tier (default + sensitivity tier schemes) | Causal statements about geography or rurality causing outcomes | Large N can make tiny differences look 'significant' — use effect sizes |
| Q2 — Distance to care vs utilization/outcomes | Distance + utilization | Access/supply proxies (healthcare_access, doctors, beds), outcomes | Access proxies only (explicitly label distance/utilization as unmeasured) | Any statement specifically about distance-to-care or utilization patterns | Proxy substitution can mislead unless the measurement gap is explicit |
| Q3 — Communities defying access assumptions | Outliers vs expectation | country-level aggregates; access proxies; outcomes | Z-scores on access vs outcomes; practical-difference checks | That an apparent outlier implies a real-world 'exceptional health system' | Tiny between-group variance inflates z-scores; absolute deltas may be noise-level |
| Q4 — Sensitivity to geographic category definitions | Definition dependence | Multiple tier schemes from urbanization_rate | Compare 3-tier vs binary vs 4-tier schemes | Tier definitions matter unless conclusions change meaningfully | If there is no signal, 'robustness' can be trivial — explain why |
| Q5 — Uncertainty from sparse reporting / small populations | Missingness + small-N instability | Group counts; CI half-widths; missingness is ~0 in this dataset | Observed CI widths + simulated sparsity via subsampling | That real-world under-reporting exists here (it is not observed) | Overinterpreting narrow CIs as 'high certainty' when data structure is synthetic |
| Q6 — What conclusions would be premature | Inference limits + confounding | Correlation structure; income/education proxies; entropy checks | Premature-conclusions framework + expected-vs-observed benchmarks (labeled illustrative) | Policy prescriptions from absent structure / near-zero dependence | Conflating benchmark expectations with observed evidence |

## Notes
- Distance-to-care and utilization are **not measured** in this dataset; we use access proxies only.
- Synthetic/low-signal structure means results are best treated as descriptive of this dataset.