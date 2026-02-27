"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  apiGetJson,
  type CountrySummaryResponse,
  type MarkdownResponse,
  type PhasesSummaryResponse
} from "@/lib/api";
import { formatNumber } from "@/lib/format";
import { DataQualityReport } from "@/components/DataQualityReport";
import { PromptGapMatrix } from "@/components/PromptGapMatrix";

function StatusPill({ ok }: { ok: boolean }) {
  return (
    <span
      className={[
        "inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold",
        ok ? "bg-emerald-900/60 text-emerald-200" : "bg-rose-900/60 text-rose-200"
      ].join(" ")}
    >
      {ok ? "OK" : "Missing"}
    </span>
  );
}

export function PhasesClient() {
  const params = useSearchParams();
  const selectedCountry = params.get("country");
  const metric = params.get("metric");
  const year = params.get("year");
  const dedup = params.get("dedup") === "true";

  const [summary, setSummary] = useState<PhasesSummaryResponse | null>(null);
  const [countrySummary, setCountrySummary] = useState<CountrySummaryResponse | null>(null);
  const [dq, setDq] = useState<MarkdownResponse | null>(null);
  const [gap, setGap] = useState<MarkdownResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGetJson<PhasesSummaryResponse>("/api/phases/summary")
      .then(setSummary)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selectedCountry) {
      setCountrySummary(null);
      return;
    }
    const qs = new URLSearchParams();
    qs.set("country", selectedCountry);
    if (year) qs.set("year", year);
    if (dedup) qs.set("dedup", "true");
    apiGetJson<CountrySummaryResponse>(`/api/country/summary?${qs.toString()}`)
      .then(setCountrySummary)
      .catch(() => setCountrySummary(null));
  }, [selectedCountry, year, dedup]);

  useEffect(() => {
    apiGetJson<MarkdownResponse>("/api/markdown/data_quality_report").then(setDq).catch(() => {});
    apiGetJson<MarkdownResponse>("/api/markdown/prompt_gap_matrix").then(setGap).catch(() => {});
  }, []);

  const context = useMemo(() => {
    return {
      country: selectedCountry ?? undefined,
      metric: metric ?? undefined,
      year: year ?? undefined,
      dedup: dedup ? "true" : undefined
    };
  }, [selectedCountry, metric, year, dedup]);

  const artifacts = summary?.artifacts ?? {};
  const tables = summary?.tables ?? {};

  return (
    <div className="space-y-6">
      {Object.values(context).some(Boolean) ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-4 text-sm">
          <div className="text-sm font-semibold">Selection Context</div>
          <div className="mt-2 font-mono text-xs text-slate-200">{JSON.stringify(context)}</div>
        </div>
      ) : null}

      {countrySummary ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm font-semibold">Country Summary</div>
            <div className="text-xs text-slate-400">{countrySummary.dedup ? "dedup" : "base"}</div>
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <div className="text-sm">
              <div className="text-slate-400">country</div>
              <div className="font-mono">{countrySummary.country}</div>
            </div>
            <div className="text-sm">
              <div className="text-slate-400">n_rows</div>
              <div className="font-mono">{formatNumber(countrySummary.n_rows)}</div>
            </div>
            <div className="text-sm">
              <div className="text-slate-400">years / diseases</div>
              <div className="font-mono">
                {formatNumber(countrySummary.n_years)} / {formatNumber(countrySummary.n_diseases)}
              </div>
            </div>
          </div>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-300">
                <tr>
                  <th className="py-2 pr-3">metric</th>
                  <th className="py-2 pr-3">avg</th>
                </tr>
              </thead>
              <tbody className="text-slate-200">
                {Object.entries(countrySummary.averages).map(([k, v]) => (
                  <tr key={k} className="border-t border-slate-800">
                    <td className="py-2 pr-3 font-mono">{k}</td>
                    <td className="py-2 pr-3">{formatNumber(v)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {error ? <div className="text-red-300">{error}</div> : null}
      {!summary ? <div className="text-sm text-slate-300">Loading…</div> : null}

      {summary ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold">Artifacts</div>
              <StatusPill ok={Boolean(artifacts.run_metadata?.exists)} />
            </div>
            <ul className="mt-3 space-y-2 text-sm text-slate-200">
              {Object.entries(artifacts).map(([k, v]) => (
                <li key={k} className="flex items-center justify-between gap-3">
                  <span className="font-mono text-xs">{k}</span>
                  <span className="text-xs text-slate-400">{v.exists ? "present" : "missing"}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold">Tables</div>
              <StatusPill ok={tables.clean_health != null} />
            </div>
            <ul className="mt-3 space-y-2 text-sm text-slate-200">
              {Object.entries(tables).map(([k, v]) => (
                <li key={k} className="flex items-center justify-between gap-3">
                  <span className="font-mono text-xs">{k}</span>
                  <span className="text-xs text-slate-300">{v == null ? "missing" : formatNumber(v)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      {summary?.robustness_delta_summary?.length ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-4">
          <div className="text-sm font-semibold">Robustness (Base vs Dedup)</div>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-300">
                <tr>
                  <th className="py-2 pr-3">view</th>
                  <th className="py-2 pr-3">base</th>
                  <th className="py-2 pr-3">dedup</th>
                  <th className="py-2 pr-3">pass</th>
                  <th className="py-2 pr-3">criteria</th>
                </tr>
              </thead>
              <tbody className="text-slate-200">
                {summary.robustness_delta_summary.map((r) => (
                  <tr key={r.view_name} className="border-t border-slate-800">
                    <td className="py-2 pr-3 font-mono">{r.view_name}</td>
                    <td className="py-2 pr-3">{formatNumber(r.base_rows)}</td>
                    <td className="py-2 pr-3">{formatNumber(r.dedup_rows)}</td>
                    <td className="py-2 pr-3">{r.pass ? "✅" : "❌"}</td>
                    <td className="py-2 pr-3 text-slate-400">{r.pass_criteria}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {/* ─── Data Quality Report (full-width, structured) ─── */}
      {dq?.markdown ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-5">
          <DataQualityReport markdown={dq.markdown} />
        </div>
      ) : null}

      {/* ─── Prompt Gap Matrix (full-width, structured) ─── */}
      {gap?.markdown ? (
        <div className="rounded border border-slate-800 bg-slate-900/40 p-5">
          <PromptGapMatrix markdown={gap.markdown} />
        </div>
      ) : null}
    </div>
  );
}
