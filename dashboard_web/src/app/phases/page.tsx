import { Suspense } from "react";
import { PhasesClient } from "@/components/PhasesClient";

export default function PhasesPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold">Pipeline Phases</h1>
        <p className="text-sm text-slate-300">
          This view reads the latest reports and table counts, plus robustness deltas.
        </p>
      </div>
      <Suspense fallback={<div className="text-slate-400">Loading…</div>}>
        <PhasesClient />
      </Suspense>
    </div>
  );
}

