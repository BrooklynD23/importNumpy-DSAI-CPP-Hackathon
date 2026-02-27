import Link from "next/link";

export default function Phase5b() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 5b: ML Diagnostic</h1>
      <p className="text-slate-300 text-sm">
        Trains random-forest models on the clean health data to probe for real-world predictive
        signal. On genuine data these models achieve meaningful R² / accuracy. On uniformly
        distributed synthetic data they find nothing — confirming our dataset has no learnable
        structure.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">reports/ml_diagnostic.json</code></li>
          <li>• Regression R² for mortality_rate, recovery_rate, dalys (5-fold CV)</li>
          <li>• Classification accuracy for disease_category vs chance baseline</li>
          <li>• Overall synthetic/real verdict</li>
        </ul>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Method</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• 10 000-row random sample from <code className="rounded bg-slate-800 px-1 text-xs">clean_health</code></li>
          <li>• RandomForestRegressor / RandomForestClassifier (50 trees, depth 5)</li>
          <li>• StandardScaler preprocessing</li>
          <li>• 5-fold cross-validation, reporting mean ± std</li>
        </ul>
      </div>

      <div className="rounded border border-blue-900 bg-blue-950/30 p-4">
        <div className="text-sm font-semibold text-blue-300 mb-1">View interactive results</div>
        <p className="text-sm text-slate-300 mb-2">
          See bar charts and the overall verdict on the dedicated ML Diagnostic page.
        </p>
        <Link
          href="/ml-diagnostic"
          className="inline-block rounded bg-blue-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-600"
        >
          Open ML Diagnostic →
        </Link>
      </div>
    </div>
  );
}
