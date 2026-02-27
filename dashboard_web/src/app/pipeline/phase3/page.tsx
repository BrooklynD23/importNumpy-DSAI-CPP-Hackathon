export default function Phase3() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 3: Clean &amp; Transform</h1>
      <p className="text-slate-300 text-sm">
        Applies the quality flags from Phase 2 to produce
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">clean_health</code> — a filtered,
        enriched copy of <code className="rounded bg-slate-800 px-1 text-xs">raw_health</code> used by
        all downstream analytical views. A
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">country_summary</code> rollup table
        is also created here.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">clean_health</code> — rows with <code className="rounded bg-slate-800 px-1 text-xs">data_quality_flag = 'ok'</code> only</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">country_summary</code> — per-country aggregates</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">access_composite</code> and <code className="rounded bg-slate-800 px-1 text-xs">access_outcome_gap</code> computed columns</li>
        </ul>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Transformations Applied</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• Rate columns clipped to [0, 1]</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">access_composite</code> = mean of healthcare_access, doctors_per_1000 (normalised), hospital_beds_per_1000 (normalised)</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">access_outcome_gap</code> = access_composite − (1 − mortality_rate)</li>
          <li>• Disease category overridden via <code className="rounded bg-slate-800 px-1 text-xs">DISEASE_CATEGORY_MAP</code> in config</li>
        </ul>
      </div>
    </div>
  );
}
