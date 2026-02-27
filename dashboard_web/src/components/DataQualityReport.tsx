"use client";

import { useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

/* ─────────────────────── types ─────────────────────── */

interface MissingnessRow {
  column: string;
  nulls: number;
  pct: number;
}

interface RangeRow {
  column: string;
  min: number;
  max: number;
  outOfRange: number;
}

interface DiseaseAuditRow {
  disease: string;
  numCategories: number;
  categories: string[];
}

interface ParsedReport {
  missingness: MissingnessRow[];
  ranges: RangeRow[];
  costIncome: { label: string; min: number; max: number; negative: number }[];
  duplicateGroups: number | null;
  diseaseAudit: DiseaseAuditRow[];
  smallNCountries: string | null;
  distinctValues: { column: string; count: number; values: string }[];
  unmappedNote: string | null;
}

/* ─────────────────────── parser ─────────────────────── */

function parseDataQualityMarkdown(md: string): ParsedReport {
  const result: ParsedReport = {
    missingness: [],
    ranges: [],
    costIncome: [],
    duplicateGroups: null,
    diseaseAudit: [],
    smallNCountries: null,
    distinctValues: [],
    unmappedNote: null,
  };

  // Missingness section
  const missRe =
    /\|\s*(\w[\w_]*)\s*\|\s*(\d+)\s*\|\s*([\d.]+)%\s*\|/g;
  let m: RegExpExecArray | null;
  while ((m = missRe.exec(md)) !== null) {
    const match = m;
    if (match[1] === "Column") continue;
    result.missingness.push({
      column: match[1],
      nulls: parseInt(match[2], 10),
      pct: parseFloat(match[3]),
    });
  }

  // Rate column ranges
  const rangeRe =
    /\|\s*([\w_]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(\d+)\s*\|/g;
  const seenRange = new Set<string>();
  while ((m = rangeRe.exec(md)) !== null) {
    const match = m;
    if (match[1] === "Column" || result.missingness.some((r) => r.column === match[1])) continue;
    if (seenRange.has(match[1])) continue;
    seenRange.add(match[1]);
    result.ranges.push({
      column: match[1],
      min: parseFloat(match[2]),
      max: parseFloat(match[3]),
      outOfRange: parseInt(match[4], 10),
    });
  }

  // Cost and income ranges
  const costRe =
    /\*\*(\w[\w_ ]+)\*\*:\s*min=([\d.]+),\s*max=([\d.]+),\s*negative=(\d+)/g;
  while ((m = costRe.exec(md)) !== null) {
    const match = m;
    result.costIncome.push({
      label: match[1],
      min: parseFloat(match[2]),
      max: parseFloat(match[3]),
      negative: parseInt(match[4], 10),
    });
  }

  // Duplicate groups
  const dupRe = /Duplicate groups.*?:\s*\*\*([,\d]+)\*\*/;
  const dupMatch = md.match(dupRe);
  if (dupMatch) {
    result.duplicateGroups = parseInt(dupMatch[1].replace(/,/g, ""), 10);
  }

  // Disease category audit
  const diseaseRe =
    /\|\s*([\w/'.\- ]+?)\s*\|\s*(\d+)\s*\|\s*(\[.*?\])\s*\|/g;
  while ((m = diseaseRe.exec(md)) !== null) {
    const match = m;
    if (match[1] === "Disease") continue;
    result.diseaseAudit.push({
      disease: match[1].trim(),
      numCategories: parseInt(match[2], 10),
      categories: JSON.parse(match[3].replace(/'/g, '"')),
    });
  }

  // Small-N
  if (md.includes("No countries with fewer than")) {
    result.smallNCountries = "none";
  }

  // Distinct values
  const dvRe =
    /- \*\*(\w[\w_]*)\*\* \((\d+)\):\s*(.+)/g;
  while ((m = dvRe.exec(md)) !== null) {
    const match = m;
    result.distinctValues.push({
      column: match[1],
      count: parseInt(match[2], 10),
      values: match[3].trim(),
    });
  }

  // Unmapped
  if (md.includes("All disease names covered")) {
    result.unmappedNote = "All disease names covered by DISEASE_CATEGORY_MAP.";
  }

  return result;
}

/* ─────────────────────── sub-components ─────────────────────── */

function StatCard({
  label,
  value,
  sub,
  accent = "emerald",
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: "emerald" | "amber" | "rose" | "sky";
}) {
  const colors: Record<string, string> = {
    emerald: "border-emerald-700/50 bg-emerald-950/30",
    amber: "border-amber-700/50 bg-amber-950/30",
    rose: "border-rose-700/50 bg-rose-950/30",
    sky: "border-sky-700/50 bg-sky-950/30",
  };
  const textColors: Record<string, string> = {
    emerald: "text-emerald-300",
    amber: "text-amber-300",
    rose: "text-rose-300",
    sky: "text-sky-300",
  };
  return (
    <div className={`rounded-lg border p-4 ${colors[accent]}`}>
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-1 text-2xl font-bold ${textColors[accent]}`}>{value}</div>
      {sub && <div className="mt-0.5 text-xs text-slate-400">{sub}</div>}
    </div>
  );
}

function SectionHeader({ title, icon }: { title: string; icon: string }) {
  return (
    <div className="flex items-center gap-2 border-b border-slate-700/60 pb-2">
      <span className="text-lg">{icon}</span>
      <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
    </div>
  );
}

function CompletnessBars({ data }: { data: MissingnessRow[] }) {
  const chartData = data.map((r) => ({
    name: r.column.replace(/_/g, " "),
    completeness: 100 - r.pct,
    col: r.column,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 24)}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 120, right: 30, top: 5, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} unit="%" />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fill: "#cbd5e1", fontSize: 11 }}
          width={115}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #475569",
            borderRadius: "8px",
            color: "#f1f5f9",
            fontSize: 12,
          }}
          formatter={(val) => [`${Number(val ?? 0).toFixed(2)}%`, "Completeness"]}
        />
        <ReferenceLine x={100} stroke="#10b981" strokeDasharray="3 3" strokeWidth={1.5} />
        <Bar dataKey="completeness" radius={[0, 4, 4, 0]} maxBarSize={18}>
          {chartData.map((entry, i) => (
            <Cell
              key={i}
              fill={entry.completeness >= 100 ? "#10b981" : entry.completeness >= 90 ? "#f59e0b" : "#ef4444"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function RangeChart({ data }: { data: RangeRow[] }) {
  const chartData = data.map((r) => ({
    name: r.column.replace(/_/g, " "),
    min: r.min,
    max: r.max,
    range: r.max - r.min,
    outOfRange: r.outOfRange,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, data.length * 40)}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 120, right: 30, top: 5, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
        <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis type="category" dataKey="name" tick={{ fill: "#cbd5e1", fontSize: 11 }} width={115} />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #475569",
            borderRadius: "8px",
            color: "#f1f5f9",
            fontSize: 12,
          }}
          formatter={(val, name) => [Number(val ?? 0).toFixed(2), String(name)]}
        />
        <Bar dataKey="min" stackId="a" fill="#334155" radius={[4, 0, 0, 4]} maxBarSize={20} />
        <Bar dataKey="range" stackId="a" fill="#38bdf8" radius={[0, 4, 4, 0]} maxBarSize={20} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/* ─────────────────────── distinct values ─────────────────────── */

function DistinctValuePills({ items }: { items: ParsedReport["distinctValues"] }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.column}>
          <button
            className="flex items-center gap-2 text-left text-sm"
            onClick={() => setExpanded(expanded === item.column ? null : item.column)}
          >
            <span className="rounded bg-sky-900/50 px-2 py-0.5 text-xs font-semibold text-sky-300">
              {item.count}
            </span>
            <span className="font-mono text-slate-200">{item.column}</span>
            <span className="text-xs text-slate-500">{expanded === item.column ? "▲" : "▼"}</span>
          </button>
          {expanded === item.column && (
            <div className="mt-1.5 flex flex-wrap gap-1.5 pl-10">
              {item.values.split(", ").map((v) => (
                <span key={v} className="rounded-full bg-slate-700/60 px-2 py-0.5 text-xs text-slate-300">
                  {v}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ─────────────────────── disease audit ─────────────────────── */

function DiseaseAuditGrid({ data }: { data: DiseaseAuditRow[] }) {
  const allCategories = useMemo(() => {
    const s = new Set<string>();
    data.forEach((d) => d.categories.forEach((c) => s.add(c)));
    return Array.from(s).sort();
  }, [data]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-amber-400">
        <span className="inline-block h-2 w-2 rounded-full bg-amber-400" />
        <span>
          Every disease maps to all {allCategories.length} original categories — column is unreliable
        </span>
      </div>
      <div className="overflow-x-auto">
        <div className="flex flex-wrap gap-1.5">
          {allCategories.map((cat) => (
            <span key={cat} className="rounded bg-amber-900/40 px-2 py-1 text-xs text-amber-200">
              {cat}
            </span>
          ))}
        </div>
      </div>
      <div className="text-xs text-slate-400">
        All {data.length} diseases assigned to all {allCategories.length} categories identically.
        Pipeline uses curated <code className="rounded bg-slate-800 px-1 text-xs">DISEASE_CATEGORY_MAP</code> instead.
      </div>
    </div>
  );
}

/* ─────────────────────── main export ─────────────────────── */

export function DataQualityReport({ markdown }: { markdown: string }) {
  const report = useMemo(() => parseDataQualityMarkdown(markdown), [markdown]);

  const totalColumns = report.missingness.length;
  const completeColumns = report.missingness.filter((r) => r.pct === 0).length;
  const totalRangeChecks = report.ranges.length;
  const rangeViolations = report.ranges.reduce((acc, r) => acc + r.outOfRange, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-slate-100">Data Quality Report</h2>
        <p className="mt-1 text-xs text-slate-400">
          Automated audit of the raw dataset — missingness, ranges, duplicates, and category reliability.
        </p>
      </div>

      {/* Summary stat cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Column Completeness"
          value={`${completeColumns}/${totalColumns}`}
          sub="columns with 0% missing"
          accent={completeColumns === totalColumns ? "emerald" : "amber"}
        />
        <StatCard
          label="Range Violations"
          value={rangeViolations}
          sub={`across ${totalRangeChecks} rate columns`}
          accent={rangeViolations === 0 ? "emerald" : "rose"}
        />
        <StatCard
          label="Duplicate Groups"
          value={report.duplicateGroups?.toLocaleString() ?? "n/a"}
          sub="country × year × disease × age × gender"
          accent={report.duplicateGroups && report.duplicateGroups > 0 ? "amber" : "emerald"}
        />
        <StatCard
          label="Small-N Countries"
          value={report.smallNCountries === "none" ? "0" : "?"}
          sub="countries with < 30 observations"
          accent="emerald"
        />
      </div>

      {/* Completeness chart */}
      <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 p-4">
        <SectionHeader title="Column Completeness" icon="📊" />
        <p className="mt-2 text-xs text-slate-400">
          Percentage of non-null values per column. Green = 100% complete.
        </p>
        <div className="mt-3">
          <CompletnessBars data={report.missingness} />
        </div>
      </div>

      {/* Range chart */}
      {report.ranges.length > 0 && (
        <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 p-4">
          <SectionHeader title="Rate Column Ranges" icon="📐" />
          <p className="mt-2 text-xs text-slate-400">
            Observed min→max for each rate column. Blue band shows the actual value range.
          </p>
          <div className="mt-3">
            <RangeChart data={report.ranges} />
          </div>
          {report.ranges.every((r) => r.outOfRange === 0) && (
            <div className="mt-2 flex items-center gap-2 text-xs text-emerald-400">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400" />
              All values within expected bounds
            </div>
          )}
        </div>
      )}

      {/* Cost & Income */}
      {report.costIncome.length > 0 && (
        <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 p-4">
          <SectionHeader title="Cost & Income Ranges" icon="💰" />
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {report.costIncome.map((ci) => (
              <div key={ci.label} className="rounded border border-slate-700/40 bg-slate-800/50 p-3">
                <div className="text-xs font-semibold text-slate-200">{ci.label.replace(/_/g, " ")}</div>
                <div className="mt-2 flex items-center gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">Min</span>{" "}
                    <span className="font-mono text-sky-300">${ci.min.toLocaleString()}</span>
                  </div>
                  <div className="h-px flex-1 bg-gradient-to-r from-sky-800 to-emerald-800" />
                  <div>
                    <span className="text-slate-400">Max</span>{" "}
                    <span className="font-mono text-emerald-300">${ci.max.toLocaleString()}</span>
                  </div>
                </div>
                <div className="mt-1 text-xs text-slate-500">
                  Negative values: {ci.negative}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disease Category Audit */}
      {report.diseaseAudit.length > 0 && (
        <div className="rounded-lg border border-amber-800/40 bg-amber-950/20 p-4">
          <SectionHeader title="Disease Category Reliability" icon="⚠️" />
          <div className="mt-3">
            <DiseaseAuditGrid data={report.diseaseAudit} />
          </div>
        </div>
      )}

      {/* Distinct Values */}
      {report.distinctValues.length > 0 && (
        <div className="rounded-lg border border-slate-700/60 bg-slate-900/50 p-4">
          <SectionHeader title="Distinct Value Inventory" icon="🏷️" />
          <p className="mt-2 text-xs text-slate-400">
            Click a column to expand and see all unique values.
          </p>
          <div className="mt-3">
            <DistinctValuePills items={report.distinctValues} />
          </div>
        </div>
      )}

      {/* Unmapped note */}
      {report.unmappedNote && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-800/40 bg-emerald-950/20 px-4 py-3 text-xs text-emerald-300">
          <span>✅</span>
          <span>{report.unmappedNote}</span>
        </div>
      )}
    </div>
  );
}
