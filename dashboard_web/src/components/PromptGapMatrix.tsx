"use client";

import { useMemo, useState } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

/* ─────────────────────── types ─────────────────────── */

interface GapRow {
  id: string;
  question: string;
  requiredConcept: string;
  measured: string;
  proxy: string;
  cannotClaim: string;
  risk: string;
}

interface ParsedGap {
  rows: GapRow[];
  notes: string[];
}

/* ─────────────────────── parser ─────────────────────── */

function parsePromptGapMarkdown(md: string): ParsedGap {
  const result: ParsedGap = { rows: [], notes: [] };

  // Match table rows - the matrix table has 6 columns after the first |
  const lines = md.split("\n");
  let inTable = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // Skip separator lines
    if (/^\|[\s\-|]+\|$/.test(trimmed)) {
      inTable = true;
      continue;
    }

    // Skip header row
    if (trimmed.startsWith("| Prompt Question")) {
      inTable = true;
      continue;
    }

    if (inTable && trimmed.startsWith("|") && trimmed.endsWith("|")) {
      const cells = trimmed
        .slice(1, -1)
        .split("|")
        .map((c) => c.trim());

      if (cells.length >= 6 && cells[0].startsWith("Q")) {
        // Extract Q number
        const idMatch = cells[0].match(/^(Q\d)/);
        result.rows.push({
          id: idMatch ? idMatch[1] : cells[0].slice(0, 2),
          question: cells[0],
          requiredConcept: cells[1],
          measured: cells[2],
          proxy: cells[3],
          cannotClaim: cells[4],
          risk: cells[5],
        });
      }
    }

    // Notes section
    if (trimmed.startsWith("- ") && md.indexOf("## Notes") < md.indexOf(trimmed)) {
      // Strip markdown bold
      result.notes.push(trimmed.slice(2).replace(/\*\*/g, ""));
    }
  }

  return result;
}

/* ─────────────────────── helpers ─────────────────────── */

function getCoverageLevel(row: GapRow): "full" | "partial" | "gap" {
  const text = (row.measured + " " + row.proxy + " " + row.cannotClaim).toLowerCase();
  if (
    text.includes("not measured") ||
    text.includes("absent") ||
    text.includes("not observed")
  ) {
    return "gap";
  }
  if (
    text.includes("proxy") ||
    text.includes("unmeasured") ||
    text.includes("explicitly label")
  ) {
    return "partial";
  }
  return "full";
}

function getRiskLevel(row: GapRow): "high" | "medium" | "low" {
  const text = row.risk.toLowerCase();
  if (text.includes("mislead") || text.includes("conflating")) return "high";
  if (text.includes("inflate") || text.includes("overinterp")) return "medium";
  return "low";
}

const coverageConfig = {
  full: { label: "Full", color: "bg-emerald-900/50 text-emerald-300 border-emerald-700/50", score: 3 },
  partial: { label: "Partial", color: "bg-amber-900/50 text-amber-300 border-amber-700/50", score: 2 },
  gap: { label: "Gap", color: "bg-rose-900/50 text-rose-300 border-rose-700/50", score: 1 },
};

const riskConfig = {
  high: { label: "High", color: "bg-rose-900/50 text-rose-300" },
  medium: { label: "Medium", color: "bg-amber-900/50 text-amber-300" },
  low: { label: "Low", color: "bg-emerald-900/50 text-emerald-300" },
};

/* ─────────────────────── sub-components ─────────────────────── */

function CoverageBadge({ level }: { level: "full" | "partial" | "gap" }) {
  const cfg = coverageConfig[level];
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

function RiskBadge({ level }: { level: "high" | "medium" | "low" }) {
  const cfg = riskConfig[level];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cfg.color}`}>
      {cfg.label} Risk
    </span>
  );
}

function QuestionCard({ row }: { row: GapRow }) {
  const [open, setOpen] = useState(false);
  const coverage = getCoverageLevel(row);
  const risk = getRiskLevel(row);

  // Extract short question title
  const shortTitle = row.question.replace(/^Q\d\s*—\s*/, "");

  return (
    <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 transition-all hover:border-slate-600/60">
      {/* Collapsed header */}
      <button
        className="flex w-full items-center justify-between p-4 text-left"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-3">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-900/50 text-sm font-bold text-sky-300">
            {row.id}
          </span>
          <div>
            <div className="text-sm font-medium text-slate-100">{shortTitle}</div>
            <div className="mt-0.5 text-xs text-slate-400">{row.requiredConcept}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <CoverageBadge level={coverage} />
          <RiskBadge level={risk} />
          <span className="ml-1 text-slate-500">{open ? "▲" : "▼"}</span>
        </div>
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="border-t border-slate-700/40 px-4 pb-4 pt-3">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Measured / Available */}
            <div className="rounded border border-slate-700/30 bg-slate-800/40 p-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-sky-400">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                What We Measure
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{row.measured}</p>
            </div>

            {/* Proxy We Use */}
            <div className="rounded border border-slate-700/30 bg-slate-800/40 p-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-amber-400">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                Proxy Used
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{row.proxy}</p>
            </div>

            {/* Cannot Claim */}
            <div className="rounded border border-rose-800/30 bg-rose-950/20 p-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-rose-400">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                </svg>
                What We Cannot Claim
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{row.cannotClaim}</p>
            </div>

            {/* Risk */}
            <div className="rounded border border-amber-800/30 bg-amber-950/20 p-3">
              <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-amber-400">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                Premature Conclusion Risk
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{row.risk}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CoverageRadar({ rows }: { rows: GapRow[] }) {
  const data = rows.map((r) => {
    const coverage = getCoverageLevel(r);
    return {
      question: r.id,
      coverage: coverageConfig[coverage].score,
      fullMark: 3,
    };
  });

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis
          dataKey="question"
          tick={{ fill: "#cbd5e1", fontSize: 13, fontWeight: 600 }}
        />
        <PolarRadiusAxis
          domain={[0, 3]}
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickCount={4}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #475569",
            borderRadius: "8px",
            color: "#f1f5f9",
            fontSize: 12,
          }}
          formatter={(val) => {
            const v = Number(val ?? 0);
            const labels = ["", "Gap", "Partial", "Full"];
            return [labels[v] || v, "Coverage"];
          }}
        />
        <Radar
          name="Coverage"
          dataKey="coverage"
          stroke="#38bdf8"
          fill="#38bdf8"
          fillOpacity={0.25}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

/* ─────────────────────── main export ─────────────────────── */

export function PromptGapMatrix({ markdown }: { markdown: string }) {
  const gap = useMemo(() => parsePromptGapMarkdown(markdown), [markdown]);

  const coverageCounts = useMemo(() => {
    const counts = { full: 0, partial: 0, gap: 0 };
    gap.rows.forEach((r) => {
      counts[getCoverageLevel(r)]++;
    });
    return counts;
  }, [gap.rows]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-slate-100">Prompt Gap Matrix</h2>
        <p className="mt-1 text-xs text-slate-400">
          Maps each competition question to what the dataset actually measures. Designed to prevent
          overclaiming and prepare for judge Q&A.
        </p>
      </div>

      {/* Top-level summary: radar + stats */}
      <div className="grid gap-4 lg:grid-cols-5">
        {/* Radar chart */}
        <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 p-4 lg:col-span-3">
          <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Coverage by Question
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" /> Full (3)
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full bg-amber-400" /> Partial (2)
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full bg-rose-400" /> Gap (1)
            </span>
          </div>
          <CoverageRadar rows={gap.rows} />
        </div>

        {/* Summary stat cards */}
        <div className="flex flex-col gap-3 lg:col-span-2">
          <div className="flex-1 rounded-lg border border-emerald-700/40 bg-emerald-950/20 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">Full Coverage</div>
            <div className="mt-1 text-3xl font-bold text-emerald-300">{coverageCounts.full}</div>
            <div className="mt-0.5 text-xs text-slate-500">questions with direct measurement</div>
          </div>
          <div className="flex-1 rounded-lg border border-amber-700/40 bg-amber-950/20 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">Partial Coverage</div>
            <div className="mt-1 text-3xl font-bold text-amber-300">{coverageCounts.partial}</div>
            <div className="mt-0.5 text-xs text-slate-500">questions using proxy columns</div>
          </div>
          <div className="flex-1 rounded-lg border border-rose-700/40 bg-rose-950/20 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">Coverage Gaps</div>
            <div className="mt-1 text-3xl font-bold text-rose-300">{coverageCounts.gap}</div>
            <div className="mt-0.5 text-xs text-slate-500">questions with unmeasured concepts</div>
          </div>
        </div>
      </div>

      {/* Question cards (accordion) */}
      <div>
        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Question Details — click to expand
        </div>
        <div className="space-y-2">
          {gap.rows.map((row) => (
            <QuestionCard key={row.id} row={row} />
          ))}
        </div>
      </div>

      {/* Notes */}
      {gap.notes.length > 0 && (
        <div className="rounded-lg border border-slate-700/40 bg-slate-800/30 p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Notes</div>
          <ul className="mt-2 space-y-1.5">
            {gap.notes.map((note, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-0.5 inline-block h-1.5 w-1.5 flex-shrink-0 rounded-full bg-slate-500" />
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
