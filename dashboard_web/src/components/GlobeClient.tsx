"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { feature } from "topojson-client";

import {
  apiGetJson,
  type CountryPointsResponse,
  type CountryPointRow,
  type FiltersResponse,
} from "@/lib/api";
import { formatNumber } from "@/lib/format";

const Globe = dynamic(() => import("react-globe.gl"), { ssr: false });

/* ---------- globe background assets (CDN) ---------- */
const EARTH_IMG =
  "//unpkg.com/three-globe/example/img/earth-night.jpg";
const EARTH_BUMP =
  "//unpkg.com/three-globe/example/img/earth-topology.png";
const COUNTRY_TOPO_URL =
  "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

/* ---------- constants ---------- */

/** Fallback so dropdowns are never blank even without the API */
const FALLBACK_METRICS = [
  "mortality_rate",
  "recovery_rate",
  "dalys",
  "healthcare_access",
  "doctors_per_1000",
  "hospital_beds_per_1000",
  "avg_treatment_cost_usd",
  "per_capita_income",
  "education_index",
  "urbanization_rate",
  "prevalence_rate",
  "incidence_rate",
];

const METRIC_LABELS: Record<string, string> = {
  mortality_rate: "Mortality Rate",
  recovery_rate: "Recovery Rate",
  dalys: "DALYs",
  healthcare_access: "Healthcare Access",
  doctors_per_1000: "Doctors per 1 000",
  hospital_beds_per_1000: "Hospital Beds per 1 000",
  avg_treatment_cost_usd: "Avg Treatment Cost (USD)",
  per_capita_income: "Per-Capita Income",
  education_index: "Education Index",
  urbanization_rate: "Urbanisation Rate",
  resource_index: "Resource Index",
  access_composite: "Access Composite",
  access_outcome_gap: "Access-Outcome Gap",
  cost_burden_ratio: "Cost Burden Ratio",
  prevalence_rate: "Prevalence Rate",
  incidence_rate: "Incidence Rate",
  improvement_in_5_years: "5-Year Improvement",
};

/**
 * Static fallback: 20 dataset countries with known centroids, value=null.
 * Rendered as gray markers whenever the API is unreachable so the globe is
 * never empty.
 */
const FALLBACK_POINTS: CountryPointRow[] = [
  { iso3: "ARG", country: "Argentina",    lat: -38.42, lon: -63.62, value: null, n_rows: 0 },
  { iso3: "AUS", country: "Australia",    lat: -25.27, lon: 133.78, value: null, n_rows: 0 },
  { iso3: "BRA", country: "Brazil",       lat: -14.24, lon: -51.93, value: null, n_rows: 0 },
  { iso3: "CAN", country: "Canada",       lat:  56.13, lon:-106.35, value: null, n_rows: 0 },
  { iso3: "CHN", country: "China",        lat:  35.86, lon: 104.20, value: null, n_rows: 0 },
  { iso3: "FRA", country: "France",       lat:  46.23, lon:   2.21, value: null, n_rows: 0 },
  { iso3: "DEU", country: "Germany",      lat:  51.17, lon:  10.45, value: null, n_rows: 0 },
  { iso3: "IND", country: "India",        lat:  20.59, lon:  78.96, value: null, n_rows: 0 },
  { iso3: "IDN", country: "Indonesia",    lat:  -0.79, lon: 113.92, value: null, n_rows: 0 },
  { iso3: "ITA", country: "Italy",        lat:  41.87, lon:  12.57, value: null, n_rows: 0 },
  { iso3: "JPN", country: "Japan",        lat:  36.20, lon: 138.25, value: null, n_rows: 0 },
  { iso3: "MEX", country: "Mexico",       lat:  23.63, lon:-102.55, value: null, n_rows: 0 },
  { iso3: "NGA", country: "Nigeria",      lat:   9.08, lon:   8.68, value: null, n_rows: 0 },
  { iso3: "RUS", country: "Russia",       lat:  61.52, lon: 105.32, value: null, n_rows: 0 },
  { iso3: "SAU", country: "Saudi Arabia", lat:  23.89, lon:  45.08, value: null, n_rows: 0 },
  { iso3: "ZAF", country: "South Africa", lat: -30.56, lon:  22.94, value: null, n_rows: 0 },
  { iso3: "KOR", country: "South Korea",  lat:  35.91, lon: 127.77, value: null, n_rows: 0 },
  { iso3: "TUR", country: "Turkey",       lat:  38.96, lon:  35.24, value: null, n_rows: 0 },
  { iso3: "GBR", country: "UK",           lat:  55.38, lon:  -3.44, value: null, n_rows: 0 },
  { iso3: "USA", country: "USA",          lat:  37.09, lon: -95.71, value: null, n_rows: 0 },
];

/* ---------- colour helpers ---------- */

/** Multi-stop heatmap: green -> yellow -> orange -> red */
function heatmapColor(t: number): string {
  const stops: [number, number, number][] = [
    [34, 197, 94],   // green-500
    [250, 204, 21],  // yellow-400
    [251, 146, 60],  // orange-400
    [239, 68, 68],   // red-500
  ];
  const n = stops.length - 1;
  const idx = Math.min(Math.floor(t * n), n - 1);
  const local = (t * n) - idx;
  const [r1, g1, b1] = stops[idx];
  const [r2, g2, b2] = stops[idx + 1];
  const r = Math.round(r1 + (r2 - r1) * local);
  const g = Math.round(g1 + (g2 - g1) * local);
  const b = Math.round(b1 + (b2 - b1) * local);
  return `rgba(${r},${g},${b},1)`;
}

function valueToNorm(
  value: number | null,
  min: number | null,
  max: number | null,
): number {
  if (value == null || !Number.isFinite(value) || min == null || max == null) return 0;
  const denom = max - min;
  const t0 = denom === 0 ? 0.5 : Math.min(1, Math.max(0, (value - min) / denom));
  return Math.pow(t0, 0.65);
}

/* ---------- sub-components ---------- */

function ColorLegend({
  min,
  max,
  label,
}: {
  min: number | null;
  max: number | null;
  label: string;
}) {
  const stops = 40;
  const gradient = Array.from({ length: stops }, (_, i) =>
    heatmapColor(i / (stops - 1)),
  ).join(", ");

  return (
    <div className="flex items-center gap-3">
      <span className="shrink-0 text-xs text-slate-400">
        {min != null ? formatNumber(min) : "\u2014"}
      </span>
      <div className="relative h-3 w-full min-w-[140px] overflow-hidden rounded-full">
        <div
          className="absolute inset-0"
          style={{ background: `linear-gradient(to right, ${gradient})` }}
        />
      </div>
      <span className="shrink-0 text-xs text-slate-400">
        {max != null ? formatNumber(max) : "\u2014"}
      </span>
      <span className="ml-1 shrink-0 text-[10px] font-medium uppercase tracking-wider text-slate-500">
        {label}
      </span>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="flex items-center gap-2 text-xs text-slate-400">
      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        />
      </svg>
      Loading\u2026
    </div>
  );
}

/* ---------- component ---------- */

export function GlobeClient() {
  const router = useRouter();
  const globeRef = useRef<any>(null);

  /* Country polygon borders (loaded once from CDN) */
  const [countries, setCountries] = useState<any[]>([]);
  useEffect(() => {
    fetch(COUNTRY_TOPO_URL)
      .then((r) => r.json())
      .then((topo) => {
        const land = feature(topo, topo.objects.countries) as any;
        setCountries(land.features);
      })
      .catch(() => {});
  }, []);

  const [filters, setFilters] = useState<FiltersResponse | null>(null);
  const [metric, setMetric] = useState<string>("mortality_rate");
  const [year, setYear] = useState<number | "all">("all");
  const [dedup, setDedup] = useState<boolean>(false);
  const [pointsResp, setPointsResp] = useState<CountryPointsResponse | null>(null);
  const [apiDown, setApiDown] = useState(false);
  const [dedupUnavailable, setDedupUnavailable] = useState(false);
  const [loadingMetric, setLoadingMetric] = useState(false);
  const [retryKey, setRetryKey] = useState(0);

  /* ---- Fetch filters ---- */
  useEffect(() => {
    apiGetJson<FiltersResponse>("/api/filters")
      .then((f) => {
        setFilters(f);
        setApiDown(false);
      })
      .catch(() => {
        setApiDown(true);
      });
  }, []);

  /* ---- Fetch point data ---- */
  useEffect(() => {
    const qs = new URLSearchParams();
    qs.set("metric", metric);
    if (year !== "all") qs.set("year", String(year));
    if (dedup) qs.set("dedup", "true");

    setLoadingMetric(true);
    setDedupUnavailable(false);

    apiGetJson<CountryPointsResponse>(
      `/api/globe/country-points?${qs.toString()}`,
    )
      .then((resp) => {
        setPointsResp(resp);
        setApiDown(false);
      })
      .catch((err: Error) => {
        // 409 = dedup table missing → fall back automatically
        if (err.message?.includes("API 409") && dedup) {
          setDedupUnavailable(true);
          setDedup(false);
          return;
        }
        // True network / 5xx failure — keep any previous data, mark offline
        setApiDown(true);
      })
      .finally(() => setLoadingMetric(false));
  }, [metric, year, dedup, retryKey]);

  /* ---- Globe styling on mount ---- */
  useEffect(() => {
    if (!globeRef.current) return;
    const globe = globeRef.current;
    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.4;
    globe.controls().enableDamping = true;
    globe.controls().dampingFactor = 0.08;
  }, [pointsResp]);

  /* ---- Derived ---- */
  const metricOptions = filters?.metrics ?? FALLBACK_METRICS;
  const yearOptions = filters?.years ?? [];
  // When API is down show fallback ghost markers so globe is never empty
  const displayPoints: CountryPointRow[] =
    pointsResp?.data && pointsResp.data.length > 0
      ? pointsResp.data
      : apiDown
      ? FALLBACK_POINTS
      : [];
  const dataCount = pointsResp?.data?.length ?? 0;
  const metricMin = pointsResp?.min ?? null;
  const metricMax = pointsResp?.max ?? null;

  /* ---- Point accessors ---- */
  const pointLat = useCallback((d: object) => (d as CountryPointRow).lat, []);
  const pointLng = useCallback((d: object) => (d as CountryPointRow).lon, []);

  const pointColor = useCallback(
    (d: object) => {
      const row = d as CountryPointRow;
      // No-data / fallback markers → muted slate
      if (row.value == null) return "rgba(100,116,139,0.55)";
      const t = valueToNorm(row.value, metricMin, metricMax);
      return heatmapColor(t);
    },
    [metricMin, metricMax],
  );

  const pointAltitude = useCallback(
    (d: object) => {
      const row = d as CountryPointRow;
      if (row.value == null) return 0.005;
      const t = valueToNorm(row.value, metricMin, metricMax);
      return 0.01 + t * 0.15;
    },
    [metricMin, metricMax],
  );

  const pointRadius = useCallback(
    (d: object) => {
      const row = d as CountryPointRow;
      const t = valueToNorm(row.value, metricMin, metricMax);
      return 0.4 + t * 0.8;
    },
    [metricMin, metricMax],
  );

  const pointLabel = useCallback(
    (d: object) => {
      const row = d as CountryPointRow;
      const valueStr = row.value == null ? "n/a" : formatNumber(row.value);
      return `
        <div style="
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          background: rgba(15,23,42,0.92);
          border: 1px solid rgba(148,163,184,0.3);
          border-radius: 8px;
          padding: 10px 14px;
          line-height: 1.5;
          color: #e2e8f0;
          min-width: 180px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        ">
          <div style="font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:4px;">${row.country}</div>
          <div style="font-size:11px;color:#94a3b8;">
            ${METRIC_LABELS[metric] ?? metric}: <span style="color:#fbbf24;font-weight:600;">${valueStr}</span>
          </div>
          <div style="font-size:10px;color:#64748b;margin-top:2px;">
            ${row.n_rows} observation${row.n_rows !== 1 ? "s" : ""} &middot; ${row.iso3}
          </div>
        </div>
      `;
    },
    [metric],
  );

  const onPointClick = useCallback(
    (d: object) => {
      const row = d as CountryPointRow;
      const qs = new URLSearchParams();
      qs.set("country", row.country);
      qs.set("metric", metric);
      if (year !== "all") qs.set("year", String(year));
      if (dedup) qs.set("dedup", "true");
      router.push(`/phases?${qs.toString()}`);
    },
    [metric, year, dedup, router],
  );

  return (
    <div className="space-y-4">
      {/* --- Top bar: controls + legend --- */}
      <div className="flex flex-wrap items-end gap-4 rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4 backdrop-blur">
        {/* Metric selector */}
        <label className="block min-w-[180px] flex-1">
          <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Metric
          </div>
          <select
            className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 transition focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/40"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
          >
            {metricOptions.map((m) => (
              <option key={m} value={m}>
                {METRIC_LABELS[m] ?? m}
              </option>
            ))}
          </select>
        </label>

        {/* Year selector */}
        <label className="block min-w-[100px]">
          <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Year
          </div>
          <select
            className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 transition focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/40"
            value={String(year)}
            onChange={(e) =>
              setYear(e.target.value === "all" ? "all" : Number(e.target.value))
            }
          >
            <option value="all">All Years</option>
            {yearOptions.map((y) => (
              <option key={y} value={String(y)}>
                {y}
              </option>
            ))}
          </select>
        </label>

        {/* Dedup toggle */}
        <label className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm transition hover:border-slate-600">
          <input
            type="checkbox"
            checked={dedup}
            onChange={(e) => setDedup(e.target.checked)}
            className="accent-cyan-500"
          />
          <span className="text-slate-300">Dedup</span>
        </label>

        {/* Status pills */}
        <div className="ml-auto flex items-center gap-3">
          {loadingMetric && <LoadingSpinner />}

          {dedupUnavailable && (
            <span className="rounded-full bg-amber-500/15 px-3 py-1 text-[11px] font-medium text-amber-400">
              Dedup unavailable &mdash; run Phase 4b
            </span>
          )}

          {apiDown && (
            <span className="flex items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-[11px] font-medium text-amber-400">
              API offline &mdash; start FastAPI on :8000
              <button
                onClick={() => { setApiDown(false); setRetryKey((k) => k + 1); }}
                className="ml-1 rounded border border-amber-500/40 px-2 py-0.5 text-[10px] hover:bg-amber-500/20 transition"
              >
                Retry
              </button>
            </span>
          )}

          {!apiDown && dataCount > 0 && (
            <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-[11px] font-medium text-emerald-400">
              {dataCount} countries
            </span>
          )}
        </div>
      </div>

      {/* --- Globe + legend area --- */}
      <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-gradient-to-b from-slate-950 via-[#0c1222] to-slate-950">
        {/* Floating metric badge */}
        <div className="absolute left-4 top-4 z-10 space-y-2">
          <div className="rounded-lg bg-slate-950/80 px-3 py-2 text-sm font-semibold text-slate-100 shadow-lg backdrop-blur-sm">
            {METRIC_LABELS[metric] ?? metric}
          </div>
          {metricMin != null && (
            <div className="w-64 rounded-lg bg-slate-950/80 px-3 py-2 shadow-lg backdrop-blur-sm">
              <ColorLegend
                min={metricMin}
                max={metricMax}
                label={metric.replace(/_/g, " ")}
              />
            </div>
          )}
        </div>

        {/* Globe canvas */}
        <div className="flex items-center justify-center py-4">
          <Globe
            ref={globeRef}
            backgroundColor="rgba(0,0,0,0)"
            globeImageUrl={EARTH_IMG}
            bumpImageUrl={EARTH_BUMP}
            showGlobe={true}
            showAtmosphere={true}
            atmosphereColor="#38bdf8"
            atmosphereAltitude={0.18}
            /* --- country polygon borders --- */
            polygonsData={countries}
            polygonCapColor={() => "rgba(0,0,0,0)"}
            polygonSideColor={() => "rgba(0,0,0,0)"}
            polygonStrokeColor={() => "rgba(148,163,184,0.35)"}
            polygonAltitude={0.005}
            /* --- data points --- */
            pointsData={displayPoints}
            pointLat={pointLat as any}
            pointLng={pointLng as any}
            pointColor={pointColor as any}
            pointAltitude={pointAltitude as any}
            pointRadius={pointRadius as any}
            pointLabel={pointLabel as any}
            onPointClick={onPointClick as any}
            width={960}
            height={680}
          />
        </div>

        {/* Bottom info row */}
        <div className="flex items-center justify-between border-t border-slate-800/60 bg-slate-950/50 px-5 py-2 text-[11px] text-slate-500">
          <span>Click a marker to drill into phase details</span>
          <span>
            Data source: DuckDB &middot;{" "}
            {dedup ? "Deduplicated" : "Standard"} view
          </span>
        </div>
      </div>
    </div>
  );
}

