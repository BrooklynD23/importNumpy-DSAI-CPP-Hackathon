# Team Q&A Preparation — DND Spring 2026 Datathon

**Team:** importNumpy
**Event:** DND Spring 2026 Datathon · Cal Poly Pomona
**Presentation:** "5 Conclusions That Would Kill Your Policy"
**Date prepared:** 2026-02-28

---

## HOW TO USE THIS DOCUMENT

Every team member reads this document before the day of presentation.
Every team member must be able to answer every question in Section 2 from memory.
The Top 3 Q&A defenses in Section 3 have full scripts — practice them aloud until they feel natural.
Section 4 lists what you must **never say** under any circumstance.

---

## 1. Executive Narrative (Memorize This First)

> "We were given a 1-million-row global health dataset and asked whether geography drives health outcome disparities. Before drawing conclusions, we ran a data integrity check. What we found is that this dataset behaves like synthetically generated data — near-zero correlations across all major variables, near-perfectly balanced factorial design, and uniform-like distributions on every bounded column. Because the dataset lacks real-world structure, any causal or policy conclusion would be premature. Instead, we present five common conclusions this data tempts you to make — and the evidence showing each one is unsupported. We also show, using literature benchmarks, what a real dataset would reveal and what responsible next steps would follow."

**Length:** ~45 seconds. Any team member can say this if asked "what's your project about?"

---

## 2. Questions Every Team Member Must Be Able to Answer

### About the Dataset

**Q: How big is your dataset?**
A: 1 million rows. 20 countries, 25 years (2000–2024), 20 diseases, 4 age groups, 3 genders — 120,000 possible combinations, 99.98% filled.

**Q: What columns does it have?**
A: Health outcomes (mortality rate, recovery rate, DALYs), access proxies (healthcare access score, doctors per 1,000, hospital beds per 1,000), socioeconomic indicators (per capita income, education index), geography proxy (urbanization rate), and structural columns (country, year, disease, age group, gender).

**Q: What is missing from the dataset?**
A: Distance-to-care, utilization data (visits, admissions), facility locations, travel time, and any real-world reporting variation or missingness. These are the variables the competition prompt specifically asks about — and they are not present.

**Q: What does "data quality is perfect" mean if the data is synthetic?**
A: Two separate things. Quality = no nulls, no out-of-range values, all rows pass validation checks. Realism = whether the statistical structure matches real-world health systems. This dataset passes quality checks but fails the realism check — six independent diagnostics confirm synthetic generation or heavy synthetic balancing.

---

### About the Synthetic Finding

**Q: Is the data synthetic?**
A: With high confidence, yes. We measured six independent signatures: near-Cartesian design coverage (99.98%), near-zero pairwise correlations across 14 variables (max |r| = 0.0023), exact match to Uniform(a,b) distributions on all bounded columns, implausibly homogeneous country profiles (mortality SD = 0.013 across 20 countries), randomized disease category labels (entropy = 3.459 vs theoretical max 3.459), and strict 2-decimal quantization on 100% of numeric values. All six point the same direction. We cannot claim absolute provenance — that requires metadata from the data provider — but the statistical evidence is unambiguous.

**Q: Why did you analyze a synthetic dataset?**
A: Two reasons. First, we did not know it was synthetic until we ran the integrity check — which is the correct order of operations. Second, the analytical frameworks are the deliverable. The pipeline, robustness checks, sensitivity analyses, and evidence-labeling system are fully transferable to a real dataset. We demonstrated the methodology; the data happened not to have signal.

**Q: Did the competition organizers tell you the data was synthetic?**
A: No. We discovered it through the data integrity pipeline. The prompt does not disclose provenance. Discovering and disclosing it is part of our analysis — it directly answers competition question Q6 ("what conclusions would be premature?").

**Q: How confident are you that the data is synthetic?**
A: Very high confidence. Any single diagnostic could be coincidence. Six independent diagnostics all consistent with synthetic generation is not coincidence. The correlation between healthcare access and mortality is 0.00008. In every peer-reviewed global health dataset, this relationship is −0.30 to −0.50. The probability of observing that gap by chance is effectively zero.

---

### About the Competition Questions

**Q: What did you find for Q1 — geographic disparities?**
A: Disparities are absent. Cohen's d for all tier pairs is below 0.01 (negligible effect). ANOVA eta-squared is 0.0000208 — geography explains 0.002% of mortality variance. The p-value is highly significant (p < 0.001) because N = 1 million, but statistical significance at that scale is meaningless. We report effect sizes, not p-values.

**Q: What did you find for Q2 — access vs outcomes?**
A: No relationship. Pearson r between healthcare access and mortality is 0.00008. R-squared is effectively zero. There is no dose-response at any decile threshold. Additionally, the two variables the prompt actually asks about — distance-to-care and utilization — are not present in the dataset. We used access proxies and disclosed this explicitly.

**Q: What did you find for Q3 — outlier communities?**
A: Some countries show high z-scores, but the absolute mortality differences are less than 0.5 percentage points — noise level. Z-scores inflate when within-group variance is near-zero, as it is here. No country deviates meaningfully in absolute terms.

**Q: What did you find for Q4 — sensitivity to tier definitions?**
A: The conclusions are robust — and that robustness is itself a finding. Three tier schemes (default 3-tier, binary, 4-tier) all produce the same result: negligible differences across groups. Maximum spread across schemes is less than 0.04 percentage points. However, we note explicitly that robustness here validates a null result, not a policy-relevant pattern.

**Q: What did you find for Q5 — sparse reporting?**
A: Not observed in this dataset. Every column has 0% missingness. All 640 subgroups exceed the minimum 30-observation threshold. Confidence intervals are uniformly narrow. We simulated what sparse reporting would look like via subsampling — removing 95% of data widens CIs dramatically. This demonstrates the methodology for real-world data where sparse reporting actually exists.

**Q: What did you find for Q6 — premature conclusions?**
A: Five specific conclusions are premature. The synthetic detection finding is itself the primary answer: any causal or policy statement linking access, geography, or income to health outcomes is unsupported because the correlational structure that would justify such claims is absent. The five traps we named are the most common conclusions a naive analyst would draw.

---

### About Methodology

**Q: Why did you use effect sizes instead of p-values?**
A: With N = 1 million, virtually every difference is statistically significant even when the effect is trivially small. A 0.001 percentage point difference in mortality has a p-value near zero — but it is not actionable. Effect sizes (Cohen's d, eta-squared) tell you whether a difference is meaningful, not just detectable.

**Q: What is the evidence ladder?**
A: A labeling system we applied to every claim. DESCRIPTIVE means "this is what the provided dataset contains." ROBUSTNESS means "this result is stable under different analytical choices." ILLUSTRATIVE means "this is a benchmark or simulation based on real-world literature, clearly labeled as not observed data." Every slide and every claim carries one of these labels so judges can trace exactly how strong each inference is.

**Q: How did you handle the deduplication issue?**
A: Each (country, year, disease, age, gender) cell appears ~8.3 times in the dataset. We compared base analytical views against dedup-at-cell-grain views for all six questions. Deltas are noise-level (< 0.001 percentage points on all metrics). Repeated sampling does not inflate any finding.

**Q: Can your pipeline run on real data?**
A: Yes. One command — `bash run.sh` — regenerates everything. The pipeline reads from DuckDB, runs 8 phases, executes 8 notebooks, and produces 30 figures and 8 HTML reports. Replacing the source CSV and re-running produces updated outputs automatically.

---

## 3. Top 3 Q&A Defenses (Full Scripts)

### Defense 1 — "Why did you keep analyzing a synthetic dataset? Doesn't that invalidate your work?"

**Script (deliver calmly, no defensiveness):**

> "That question assumes we knew the data was synthetic before we analyzed it — we didn't. Discovering the synthetic structure was the first finding, not a starting assumption.
>
> More importantly, the question of whether a dataset is real or synthetic is separate from whether the analytical method is valid. Our pipeline — the data quality checks, robustness tests, sensitivity analyses, evidence labeling system — is the same methodology you would apply to a real dataset. We demonstrated it on this data.
>
> What the synthetic structure does invalidate is causal or policy claims. It does not invalidate the analytical framework. We explicitly labeled every finding as DESCRIPTIVE of this dataset and avoided prescribing real-world interventions. That distinction is the center of our entire presentation.
>
> The question we answered is: given this dataset, what conclusions would be premature? The answer is: all of them — and we showed exactly why."

---

### Defense 2 — "You can't answer Q2. Distance-to-care isn't in your data. Doesn't that mean you failed the prompt?"

**Script (lead with the policy framing):**

> "We disagree with the premise. Answering a question by specifying what data is missing and what would be required to answer it properly is not failure — it is the most responsible form of analysis.
>
> A team that invents an answer to Q2 using access proxies while hiding the measurement gap is providing a misleading result. We chose to be explicit: distance-to-care is not measured here, the proxies we used correlate with mortality at r = 0.00008, and no inference about distance-driven disparities is supportable from this dataset.
>
> We then did something beyond what the prompt required: we specified exactly what a properly instrumented dataset would need — travel time, facility density, utilization records — and showed what the analysis would look like if those variables existed, using literature benchmarks.
>
> Disclosing a measurement gap and specifying how to close it is precisely the analytical posture that prevents bad policy. We answered Q2 by showing what honest analysis of an inadequate dataset looks like."

---

### Defense 3 — "How do you know the data is synthetic and not just unusually clean real data?"

**Script (lead with the correlation argument — it's the most powerful):**

> "This is the right question to ask, and we have a specific answer.
>
> The decisive evidence is the correlation between healthcare access and mortality: r = 0.00008. In every published global health dataset we examined — WHO, Lancet, World Bank — this relationship is between −0.30 and −0.50. The probability of observing r = 0.00008 in real-world health data collected across 20 countries over 25 years is effectively zero.
>
> That one finding would be enough. But we measured five others: near-Cartesian design coverage of 99.98%, bounded-column distributions that match Uniform(a,b) expectations to less than 0.01% error, country-level mortality standard deviation of 0.013 — impossibly homogeneous for 20 real countries — randomized disease category labels with entropy at the theoretical maximum, and strict 2-decimal quantization on 100% of numeric values.
>
> Any single one of those could occur by chance. All six, simultaneously, in the same direction — that is not real data. We cannot claim absolute provenance without metadata from the data provider, and we said so explicitly. But the statistical conclusion is not in doubt."

---

## 4. What to NEVER Say

| Do NOT say | Say instead |
|-----------|-------------|
| "The data is bad / low quality" | "The data is clean but exhibits synthetic structure" |
| "We couldn't answer the questions" | "We answered the questions the data can support" |
| "Distance to care is basically healthcare access" | "Distance-to-care is not measured; we use access proxies and label this explicitly" |
| "The p-value shows significance" | "The effect size is negligible; p-values are not interpretable at N=1M" |
| "Country X has better outcomes" | "Country X shows higher z-scores, but the absolute difference is less than 0.5pp" |
| "We recommend reallocating resources to..." | "The data does not support resource allocation decisions; here are the data requirements that would" |
| "We proved causality" | We never claim causality. Any causal language is banned. |
| "We think the data might be synthetic" | "Six independent diagnostics confirm synthetic structure with high confidence" |

---

## 5. Evidence Reference Card (for Q&A)

| Claim | Evidence | File |
|-------|---------|------|
| Dataset is synthetic | 6 diagnostics listed in Section 2 | `docs/dataset_audit_finding_overview.md` |
| Geographic disparities absent | η² = 0.0000208, Cohen's d < 0.01 | `reports/q1_outcome_geography.html` |
| Access↔outcome relationship | r = 0.00008, R² < 0.000001 | `reports/q2_access_vs_outcomes.html` |
| Distance-to-care unmeasured | Not in column list | `docs/prompt_to_data_contract.md` |
| Country outliers are noise | Absolute diff < 0.5pp | `reports/q3_outlier_communities.html` |
| Tier robustness | Max spread < 0.04pp | `reports/q4_sensitivity_tiers.html` |
| Sparsity not observed | 0% missingness, all groups ≥ 30 | `reports/data_quality_report.md` |
| Dedup check passed | All deltas < 0.001pp | `reports/summary_executive.html` |
| Expected vs observed gap | 8-pair dumbbell chart | `reports/figures/bench_q6_dumbbell_correlations.png` |

---

## 6. Presentation Timing

| Segment | Slides | Time |
|---------|--------|------|
| Title + stakes hook | 1–2 | 1 min |
| Data integrity reveal | 3–4 | 2 min |
| Trap #1 (rural outcomes) | 5 | 1.5 min |
| Trap #2 (access↔outcomes) | 6 | 1.5 min |
| Trap #3 (outliers) | 7 | 1 min |
| Trap #4 (tier sensitivity) | 8 | 1 min |
| Trap #5 (sparse reporting) | 9 | 1 min |
| Robustness + benchmark | 10–11 | 1.5 min |
| Action plan + close | 12 | 1 min |
| **Total** | | **~12 min** |

Target 8 minutes for content, leave 2–4 minutes for Q&A buffer within the 8+4 window.

---

## 7. Final Prep Checklist

- [ ] Every team member has read this document
- [ ] Every team member can deliver the 45-second executive narrative (Section 1) without notes
- [ ] Every team member has practiced Defense 1, 2, and 3 aloud at least twice
- [ ] Assigned speaker for each trap slide (1 person per trap)
- [ ] Slide handoff signals rehearsed (know when to pass the clicker)
- [ ] All team members know: NEVER claim causality, NEVER claim we can't answer questions, ALWAYS label evidence type
- [ ] PowerPoint verified to open on presentation laptop
- [ ] Backup copy on USB and email
