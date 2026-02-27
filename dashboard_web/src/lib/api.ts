export type LatestRunResponse = {
  run: null | {
    generated_at?: string;
    git_commit?: string | null;
    db_path?: string;
    total_seconds?: number;
    packages?: Record<string, string | null>;
  };
  db_path: string;
  reports_dir: string;
  artifacts: Record<
    string,
    { exists: boolean; path: string; mtime: string | null; size: number | null }
  >;
};

export type FiltersResponse = {
  years: number[];
  disease_categories: string[];
  disease_names: string[];
  age_groups: string[];
  genders: string[];
  metrics: string[];
  tables: Record<string, boolean>;
};

export type CountryMetricRow = { country: string; value: number | null; n_rows: number };
export type CountryMetricResponse = {
  metric: string;
  dedup: boolean;
  filters: Record<string, unknown>;
  min: number | null;
  max: number | null;
  data: CountryMetricRow[];
};

export type CountryPointRow = {
  iso3: string;
  country: string;
  lat: number;
  lon: number;
  value: number | null;
  n_rows: number;
};
export type CountryPointsResponse = {
  metric: string;
  dedup: boolean;
  filters: Record<string, unknown>;
  min: number | null;
  max: number | null;
  data: CountryPointRow[];
  resolve_stats?: { resolved: number; unresolved: number };
};

export type RobustnessRow = {
  view_name: string;
  base_rows: number;
  dedup_rows: number;
  pass: boolean;
  pass_criteria: string;
};

export type PhasesSummaryResponse = {
  run: LatestRunResponse["run"];
  artifacts: LatestRunResponse["artifacts"];
  tables: Record<string, number | null>;
  robustness_delta_summary: RobustnessRow[];
};

export type MarkdownResponse = { name: string; path: string; markdown: string };

export type CountrySummaryResponse = {
  country: string;
  dedup: boolean;
  n_rows: number;
  n_years: number;
  n_diseases: number;
  averages: Record<string, number | null>;
};

export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function apiGetJson<T>(path: string): Promise<T> {
  const url = path.startsWith("http") ? path : `${apiBaseUrl}${path}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}
