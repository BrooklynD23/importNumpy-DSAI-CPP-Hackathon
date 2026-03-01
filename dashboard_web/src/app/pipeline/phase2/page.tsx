export default function Phase2() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 2: Data Quality Profiling</h1>
      <p className="text-slate-300 text-sm">
        Audits every column in <code className="mx-1 rounded bg-slate-800 px-1 text-xs">raw_health</code> for
        completeness, range violations, impossible combinations, and structural anomalies. Each row is
        tagged with a <code className="mx-1 rounded bg-slate-800 px-1 text-xs">data_quality_flag</code>{" "}
        (<em>ok</em> / <em>warn</em> / <em>fail</em>). All downstream views filter to{" "}
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">data_quality_flag = 'ok'</code>.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">reports/data_quality_report.md</code> — human-readable audit</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">reports/assumption_log.csv</code> — machine-readable assumption log</li>
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">data_quality_flag</code> column added to DuckDB</li>
        </ul>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Checks Performed</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• Rate columns clamped to [0, 1] range</li>
          <li>• Null / missing value counts per column</li>
          <li>• Duplicate row detection</li>
          <li>• Cross-column consistency (mortality + recovery &le; 1)</li>
          <li>• Year range plausibility (1990–2023)</li>
        </ul>
      </div>
    </div>
  );
}
