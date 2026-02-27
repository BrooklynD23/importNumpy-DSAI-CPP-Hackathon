"use client";

import { useEffect, useState } from "react";

import { apiGetJson, type LatestRunResponse } from "@/lib/api";

export function LatestRunCard() {
  const [data, setData] = useState<LatestRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGetJson<LatestRunResponse>("/api/run/latest")
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">Most Recent Run</div>
        <div className="text-xs text-slate-400">source: reports/_run_metadata.json</div>
      </div>

      {error ? <div className="mt-2 text-sm text-red-300">{error}</div> : null}
      {!data ? <div className="mt-2 text-sm text-slate-300">Loading…</div> : null}

      {data ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div className="text-sm">
            <div className="text-slate-400">generated_at</div>
            <div className="font-mono text-slate-100">{data.run?.generated_at ?? "n/a"}</div>
          </div>
          <div className="text-sm">
            <div className="text-slate-400">git_commit</div>
            <div className="font-mono text-slate-100">{data.run?.git_commit ?? "n/a"}</div>
          </div>
          <div className="text-sm">
            <div className="text-slate-400">db_path</div>
            <div className="font-mono text-slate-100">{data.run?.db_path ?? data.db_path}</div>
          </div>
          <div className="text-sm">
            <div className="text-slate-400">total_seconds</div>
            <div className="font-mono text-slate-100">
              {data.run?.total_seconds != null ? Number(data.run.total_seconds).toFixed(1) : "n/a"}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

