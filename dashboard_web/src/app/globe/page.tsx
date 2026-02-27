import { GlobeClient } from "@/components/GlobeClient";

export default function GlobePage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Global Health Heatmap</h1>
        <p className="text-sm text-slate-400">
          Interactive 3-D choropleth. Countries are coloured{" "}
          <span className="font-medium text-emerald-400">green</span>{" "}
          <span className="text-yellow-400">{"\u2192"}</span>{" "}
          <span className="font-medium text-red-400">red</span>{" "}
          by selected metric. Hover for details; click to drill down.
        </p>
      </div>
      <GlobeClient />
    </div>
  );
}

