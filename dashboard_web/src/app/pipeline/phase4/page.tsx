export default function Phase4() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 4: Analytical Views</h1>
      <p className="text-slate-300 text-sm">
        Builds six DuckDB views — one per competition question — from
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">clean_health</code>. Each view
        enforces a minimum observation count of 30 per group to suppress statistically
        unreliable cells.
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        {[
          { view: "v_outcome_by_geography", q: "Q1", label: "Outcome disparities by geography" },
          { view: "v_access_vs_outcomes", q: "Q2", label: "Access vs outcomes correlation" },
          { view: "v_outlier_communities", q: "Q3", label: "Outlier community detection" },
          { view: "v_sensitivity_tiers", q: "Q4", label: "Sensitivity to tier definitions" },
          { view: "v_sparse_reporting", q: "Q5", label: "Sparse reporting & uncertainty" },
          { view: "v_premature_conclusions", q: "Q6", label: "Premature conclusions guard" },
        ].map(({ view, q, label }) => (
          <div key={view} className="rounded border border-slate-700 bg-slate-900/40 p-3">
            <div className="text-xs font-semibold text-blue-400 mb-1">{q}</div>
            <div className="text-sm font-medium text-slate-200">{label}</div>
            <div className="text-xs font-mono text-slate-500 mt-1">{view}</div>
          </div>
        ))}
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Shared Constraints</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• Minimum 30 observations per group (<code className="rounded bg-slate-800 px-1 text-xs">SMALL_N_THRESHOLD</code>)</li>
          <li>• Grouped by country × year × disease_category</li>
          <li>• All views read from <code className="rounded bg-slate-800 px-1 text-xs">clean_health</code> only</li>
        </ul>
      </div>
    </div>
  );
}
