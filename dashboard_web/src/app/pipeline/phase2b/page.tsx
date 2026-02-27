export default function Phase2b() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 2b: Synthetic Signature Detection</h1>
      <p className="text-slate-300 text-sm">
        Computes statistical fingerprints that are distinctive of synthetically generated data:
        near-perfect uniformity across distributions, suspiciously round numbers, and
        cross-column correlations that collapse to zero. Results are written to a JSON report
        consumed by the ML Diagnostic phase.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">reports/synthetic_signatures.json</code></li>
          <li>• Per-column uniformity scores (KS-statistic vs uniform distribution)</li>
          <li>• Cross-column Pearson correlation matrix summary</li>
        </ul>
      </div>

      <div className="rounded border border-yellow-900 bg-yellow-950/30 p-4">
        <div className="text-sm font-semibold text-yellow-300 mb-1">Why this matters for the competition</div>
        <p className="text-sm text-slate-300">
          Demonstrating awareness that the data is synthetic — and quantifying exactly how synthetic it
          is — earns credibility with judges. It shows the team understands the limitations of the
          dataset before drawing any conclusions.
        </p>
      </div>
    </div>
  );
}
