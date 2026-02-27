"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiBaseUrl, apiGetJson, type LatestRunResponse } from "@/lib/api";

export function AnalysisClient() {
  const [data, setData] = useState<LatestRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGetJson<LatestRunResponse>("/api/run/latest")
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  const reportsBase = `${apiBaseUrl}/reports`;

  return (
    <div className="space-y-4">
      {error ? <div className="text-red-300">{error}</div> : null}

      <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold">Executive Summary</div>
        <div className="mt-3 aspect-[16/10] w-full overflow-hidden rounded border border-slate-800 bg-black">
          <iframe className="h-full w-full" src={`${reportsBase}/summary_executive.html`} />
        </div>
        <div className="mt-2 text-xs text-slate-400">
          If the iframe is blank, regenerate notebook HTML outputs on a normal local machine (sockets required).
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {[
          "q1_outcome_geography",
          "q2_access_vs_outcomes",
          "q3_outlier_communities",
          "q4_sensitivity_tiers",
          "q5_sparse_reporting",
          "q6_premature_conclusions",
          "benchmark_comparison"
        ].map((name) => (
          <Link
            key={name}
            href={`${reportsBase}/${name}.html`}
            target="_blank"
            className="rounded border border-slate-800 bg-slate-900/40 p-4 hover:border-slate-700"
          >
            <div className="text-sm font-semibold">{name}</div>
            <div className="mt-1 text-sm text-slate-300">Open HTML report</div>
          </Link>
        ))}
      </div>

      {data?.artifacts ? (
        <div className="text-xs text-slate-400">
          Latest run: {data.run?.generated_at ?? "n/a"} (commit {data.run?.git_commit ?? "n/a"})
        </div>
      ) : null}
    </div>
  );
}

