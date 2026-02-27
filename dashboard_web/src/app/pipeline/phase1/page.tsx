export default function Phase1() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Phase 1: Data Ingest</h1>
      <p className="text-slate-300 text-sm">
        Reads the raw CSV file (1 M rows × 25 columns) and loads it verbatim into DuckDB as the
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">raw_health</code> table. Two
        derived columns are appended during ingest:
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">urbanization_tier</code> (Rural /
        Peri-urban / Urban) and
        <code className="mx-1 rounded bg-slate-800 px-1 text-xs">resource_index</code>, a composite
        of healthcare access, doctors per 1 000, and hospital beds per 1 000.
      </p>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4 space-y-3">
        <div className="text-sm font-semibold">Key Outputs</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• DuckDB table: <code className="rounded bg-slate-800 px-1 text-xs">raw_health</code> (1 000 000 rows, immutable)</li>
          <li>• Added <code className="rounded bg-slate-800 px-1 text-xs">urbanization_tier</code> column (Rural / Peri-urban / Urban)</li>
          <li>• Added <code className="rounded bg-slate-800 px-1 text-xs">resource_index</code> composite score</li>
        </ul>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900/40 p-4">
        <div className="text-sm font-semibold mb-2">Design Decisions</div>
        <ul className="text-sm text-slate-300 space-y-1">
          <li>• <strong>Immutability:</strong> raw_health is never overwritten after creation — it is the ground truth.</li>
          <li>• <strong>Disease Category override:</strong> the original CSV column is unreliable; a hand-curated map in <code className="rounded bg-slate-800 px-1 text-xs">config.py</code> replaces it.</li>
          <li>• <strong>Snake_case:</strong> all column names are normalised to snake_case on load.</li>
        </ul>
      </div>

      <div className="rounded border border-blue-900 bg-blue-950/30 p-4">
        <div className="text-sm font-semibold text-blue-300 mb-1">Why DuckDB?</div>
        <p className="text-sm text-slate-300">
          DuckDB is an in-process analytical database that handles 1 M rows with zero server
          setup. SQL queries run in milliseconds directly from Python, making it ideal for
          hackathon pipelines that need to be reproducible on any laptop.
        </p>
      </div>
    </div>
  );
}
