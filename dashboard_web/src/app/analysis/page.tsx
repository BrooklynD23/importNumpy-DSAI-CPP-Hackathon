import { AnalysisClient } from "@/components/AnalysisClient";

export default function AnalysisPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Analysis Overview</h1>
        <p className="text-sm text-slate-300">
          The notebook HTML outputs are served by the local API under <code className="rounded bg-slate-900 px-1">/reports</code>.
        </p>
      </div>
      <AnalysisClient />
    </div>
  );
}

