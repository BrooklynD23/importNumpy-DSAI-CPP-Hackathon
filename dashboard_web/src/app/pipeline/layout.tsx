"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const phases = [
  { id: "1", name: "Ingest", path: "/pipeline/phase1" },
  { id: "2", name: "Profile", path: "/pipeline/phase2" },
  { id: "2b", name: "Synthetic", path: "/pipeline/phase2b" },
  { id: "3", name: "Clean", path: "/pipeline/phase3" },
  { id: "4", name: "Views", path: "/pipeline/phase4" },
  { id: "4b", name: "Robustness", path: "/pipeline/phase4b" },
  { id: "5", name: "Gap Matrix", path: "/pipeline/phase5" },
  { id: "5b", name: "ML Diagnostic", path: "/pipeline/phase5b" },
];

export default function PipelineLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
      <nav className="rounded border border-slate-800 bg-slate-900/40 p-4 h-fit">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Pipeline Phases
        </div>
        <div className="space-y-1">
          <Link
            href="/pipeline"
            className={[
              "block px-3 py-2 rounded text-sm",
              pathname === "/pipeline"
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800",
            ].join(" ")}
          >
            Overview
          </Link>
          {phases.map((phase) => (
            <Link
              key={phase.id}
              href={phase.path}
              className={[
                "block px-3 py-2 rounded text-sm",
                pathname === phase.path
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800",
              ].join(" ")}
            >
              Phase {phase.id}: {phase.name}
            </Link>
          ))}
        </div>
      </nav>
      <div className="rounded border border-slate-800 bg-slate-900/40 p-6">
        {children}
      </div>
    </div>
  );
}
