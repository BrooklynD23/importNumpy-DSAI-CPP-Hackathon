import Link from "next/link";

import { LatestRunCard } from "@/components/LatestRunCard";

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">Latest Run Dashboard</h1>
        <p className="text-slate-300">
          This app reads from <code className="rounded bg-slate-900 px-1">reports/</code> and{" "}
          <code className="rounded bg-slate-900 px-1">data/health.duckdb</code> produced by the pipeline.
        </p>
      </div>

      <LatestRunCard />

      <div className="grid gap-3 sm:grid-cols-3">
        <Link
          href="/globe"
          className="rounded border border-slate-800 bg-slate-900/40 p-4 hover:border-slate-700"
        >
          <div className="text-sm font-semibold">3D Globe</div>
          <div className="mt-1 text-sm text-slate-300">Explore per-country metrics on a globe.</div>
        </Link>
        <Link
          href="/phases"
          className="rounded border border-slate-800 bg-slate-900/40 p-4 hover:border-slate-700"
        >
          <div className="text-sm font-semibold">Phase Dashboard</div>
          <div className="mt-1 text-sm text-slate-300">Inspect outputs phase-by-phase.</div>
        </Link>
        <Link
          href="/analysis"
          className="rounded border border-slate-800 bg-slate-900/40 p-4 hover:border-slate-700"
        >
          <div className="text-sm font-semibold">Analysis Overview</div>
          <div className="mt-1 text-sm text-slate-300">Open the executive summary + notebooks.</div>
        </Link>
      </div>
    </div>
  );
}

