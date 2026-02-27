"use client";

import { useEffect, useState } from "react";
import { apiGetJson, type PhasesSummaryResponse } from "@/lib/api";
import Link from "next/link";

const PHASE_DEFS = [
  {
    id: "1",
    name: "Ingest",
    path: "/pipeline/phase1",
    table: "raw_health",
    description: "Load CSV into DuckDB",
  },
  {
    id: "2",
    name: "Profile",
    path: "/pipeline/phase2",
    artifact: "data_quality_report",
    description: "Check data quality",
  },
  {
    id: "2b",
    name: "Synthetic",
    path: "/pipeline/phase2b",
    artifact: "synthetic_signatures",
    description: "Detect synthetic patterns",
  },
  {
    id: "3",
    name: "Clean",
    path: "/pipeline/phase3",
    table: "clean_health",
    description: "Filter and transform",
  },
  {
    id: "4",
    name: "Views",
    path: "/pipeline/phase4",
    table: "v_outcome_by_geography",
    description: "Build analytical views",
  },
  {
    id: "4b",
    name: "Robustness",
    path: "/pipeline/phase4b",
    table: "robustness_delta_summary",
    description: "Dedup-at-cell robustness checks",
  },
  {
    id: "5",
    name: "Gap Matrix",
    path: "/pipeline/phase5",
    artifact: "prompt_gap_matrix",
    description: "Map prompt to data coverage",
  },
  {
    id: "5b",
    name: "ML Diagnostic",
    path: "/pipeline/phase5b",
    artifact: "ml_diagnostic",
    description: "Prove synthetic data via ML probes",
  },
];

export default function PipelineOverview() {
  const [data, setData] = useState<PhasesSummaryResponse | null>(null);

  useEffect(() => {
    apiGetJson<PhasesSummaryResponse>("/api/phases/summary")
      .then(setData)
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Pipeline Overview</h1>
        <p className="text-slate-300 mt-2 text-sm">
          Eight phases transform raw health statistics into analytical views, quality
          reports, and ML diagnostics. Each phase has a verification gate — the pipeline
          halts on failure.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {PHASE_DEFS.map((phase) => {
          const tableCount =
            phase.table && data?.tables ? data.tables[phase.table] : undefined;
          const artifactExists =
            phase.artifact && data?.artifacts
              ? data.artifacts[phase.artifact]?.exists
              : undefined;
          const isComplete =
            tableCount != null ? tableCount > 0 : artifactExists === true;
          const unknown = tableCount === undefined && artifactExists === undefined;

          return (
            <Link
              key={phase.id}
              href={phase.path}
              className={[
                "rounded border p-4 block hover:opacity-90 transition-opacity",
                isComplete
                  ? "border-green-700 bg-green-900/20"
                  : unknown
                  ? "border-slate-700 bg-slate-900/40"
                  : "border-red-800 bg-red-900/20",
              ].join(" ")}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={[
                    "w-2.5 h-2.5 rounded-full flex-shrink-0",
                    isComplete
                      ? "bg-green-500"
                      : unknown
                      ? "bg-slate-600"
                      : "bg-red-500",
                  ].join(" ")}
                />
                <div className="text-xs font-semibold text-slate-400">
                  Phase {phase.id}
                </div>
              </div>
              <div className="text-sm font-semibold text-slate-100">{phase.name}</div>
              <div className="text-xs text-slate-400 mt-1">{phase.description}</div>
              {tableCount != null && (
                <div className="text-xs font-mono text-slate-500 mt-2">
                  {tableCount.toLocaleString()} rows
                </div>
              )}
            </Link>
          );
        })}
      </div>

      {data?.run && (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
          <div className="text-sm font-semibold mb-3">Latest Pipeline Run</div>
          <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <div>
              <div className="text-xs text-slate-400">Generated</div>
              <div className="font-mono text-xs mt-0.5">
                {data.run.generated_at
                  ? new Date(data.run.generated_at).toLocaleString()
                  : "Unknown"}
              </div>
            </div>
            {data.run.total_seconds != null && (
              <div>
                <div className="text-xs text-slate-400">Duration</div>
                <div className="font-mono text-xs mt-0.5">
                  {data.run.total_seconds}s
                </div>
              </div>
            )}
            {data.run.git_commit && (
              <div>
                <div className="text-xs text-slate-400">Git Commit</div>
                <div className="font-mono text-xs mt-0.5">
                  {data.run.git_commit.substring(0, 8)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
