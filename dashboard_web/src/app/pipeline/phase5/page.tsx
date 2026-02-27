export default function Phase5() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 5: Prompt Gap Matrix</h1>
      <p className="text-slate-300 text-sm">
        Maps every competition question (prompt) to the columns and tables that directly answer it,
        identifies gaps where the data is insufficient or ambiguous, and outputs a structured
        Markdown matrix used in the presentation.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <code className="rounded bg-slate-800 px-1 text-xs">reports/prompt_gap_matrix.md</code> — Markdown table</li>
          <li>• Per-question coverage rating (Full / Partial / Gap)</li>
          <li>• Recommended caveats for each gap</li>
        </ul>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Gap Categories</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <strong className="text-green-400">Full</strong> — data directly answers the question</li>
          <li>• <strong className="text-yellow-400">Partial</strong> — data partially addresses it; caveats required</li>
          <li>• <strong className="text-red-400">Gap</strong> — data does not support the question; must be flagged</li>
        </ul>
      </div>

      <div className="rounded border border-yellow-900 bg-yellow-950/30 p-4">
        <div className="text-sm font-semibold text-yellow-300 mb-1">Competition relevance</div>
        <p className="text-sm text-slate-300">
          Explicitly documenting what the data <em>cannot</em> answer is as important as the
          analysis itself. Judges reward teams that avoid over-claiming — the gap matrix is our
          auditable evidence of intellectual honesty.
        </p>
      </div>
    </div>
  );
}
