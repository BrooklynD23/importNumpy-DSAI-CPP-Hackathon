"use client";

import { useEffect, useState } from "react";
import { apiGetJson } from "@/lib/api";

type RegressionProbe = {
  target: string;
  cv_r2_mean: number;
  cv_r2_std: number;
  verdict: string;
};

type ClassificationProbe = {
  target: string;
  cv_accuracy_mean: number;
  cv_accuracy_std: number;
  chance_accuracy: number;
  verdict: string;
};

type OverallVerdict = {
  conclusion: string;
  all_regression_near_zero: boolean;
  classification_at_chance: boolean;
};

type MLDiagnosticResponse = {
  n_rows_sampled: number;
  cv_folds: number;
  features: string[];
  regression_probes: RegressionProbe[];
  classification_probe: ClassificationProbe;
  overall_verdict: OverallVerdict;
};

export default function MLDiagnostic() {
  const [data, setData] = useState<MLDiagnosticResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGetJson<MLDiagnosticResponse>("/api/ml-diagnostic")
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  if (error)
    return (
      <div className="rounded border border-red-800 bg-red-900/20 p-4 text-red-300">
        {error.includes("404")
          ? "ML diagnostic not found — run the pipeline first (bash run.sh)."
          : `Error: ${error}`}
      </div>
    );
  if (!data)
    return <div className="text-slate-400 animate-pulse">Loading ML diagnostic…</div>;

  const isGoodNews =
    data.overall_verdict.all_regression_near_zero &&
    data.overall_verdict.classification_at_chance;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">ML Diagnostic: Proving Synthetic Data</h1>
        <p className="text-slate-300 text-sm">
          Machine learning models trained on real health data find meaningful patterns.
          On uniformly distributed synthetic data they find <em>nothing</em> — confirming our
          dataset is artificially generated.
          Probed on <span className="font-mono text-slate-200">{data.n_rows_sampled.toLocaleString()}</span> rows
          with <span className="font-mono text-slate-200">{data.cv_folds}</span>-fold cross-validation.
        </p>
      </div>

      {/* Regression Probes */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-5">
        <h2 className="text-lg font-semibold mb-4">Regression Probes — R² Scores</h2>
        <p className="text-xs text-slate-400 mb-4">
          R² = 1.0 means perfect prediction; R² ≈ 0 means the model learns nothing.
          Expected on synthetic data: near-zero.
        </p>
        <div className="space-y-4">
          {data.regression_probes.map((probe) => {
            const pct = Math.max(Math.abs(probe.cv_r2_mean) * 1000, 2);
            const isNearZero = probe.cv_r2_mean < 0.02;
            return (
              <div key={probe.target}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-mono text-slate-200">{probe.target}</span>
                  <span className={`text-sm font-semibold ${isNearZero ? "text-green-400" : "text-yellow-400"}`}>
                    R² = {probe.cv_r2_mean.toFixed(4)} ± {probe.cv_r2_std.toFixed(4)}
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded h-3 mb-1">
                  <div
                    className={`h-full rounded ${isNearZero ? "bg-green-600" : "bg-yellow-500"}`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-slate-400">{probe.verdict}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Classification Probe */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-5">
        <h2 className="text-lg font-semibold mb-4">Disease Classification Probe</h2>
        <p className="text-xs text-slate-400 mb-4">
          Can a model predict disease category from health metrics better than random guessing?
          Expected on synthetic data: at-chance accuracy.
        </p>
        <div className="grid grid-cols-2 gap-6 mb-4">
          <div className="text-center rounded border border-slate-700 p-4">
            <div className={`text-3xl font-bold ${
              data.classification_probe.cv_accuracy_mean / data.classification_probe.chance_accuracy < 1.10
                ? "text-green-400"
                : "text-yellow-400"
            }`}>
              {(data.classification_probe.cv_accuracy_mean * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-slate-300 mt-1">Model Accuracy</div>
            <div className="text-xs text-slate-500">±{(data.classification_probe.cv_accuracy_std * 100).toFixed(1)}%</div>
          </div>
          <div className="text-center rounded border border-slate-700 p-4">
            <div className="text-3xl font-bold text-slate-500">
              {(data.classification_probe.chance_accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-slate-300 mt-1">Chance Baseline</div>
            <div className="text-xs text-slate-500">random guessing</div>
          </div>
        </div>
        <div className="text-sm text-slate-400">{data.classification_probe.verdict}</div>
      </div>

      {/* Overall Verdict */}
      <div className={`rounded border p-5 ${
        isGoodNews
          ? "border-green-700 bg-green-900/20"
          : "border-yellow-700 bg-yellow-900/20"
      }`}>
        <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <span className={isGoodNews ? "text-green-400" : "text-yellow-400"}>
            {isGoodNews ? "✓" : "⚠"}
          </span>
          Overall Conclusion
        </h2>
        <p className={`text-sm ${isGoodNews ? "text-green-200" : "text-yellow-200"}`}>
          {data.overall_verdict.conclusion}
        </p>
      </div>

      {/* Features Used */}
      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <h2 className="text-sm font-semibold text-slate-400 mb-2">Features Used as Predictors</h2>
        <div className="flex flex-wrap gap-2">
          {data.features.map((f) => (
            <span key={f} className="rounded bg-slate-800 px-2 py-1 text-xs font-mono text-slate-300">
              {f}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
