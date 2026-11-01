import type { SemanticAnalysis } from "../types";

type SemanticAnalysisCardProps = {
  analysis: SemanticAnalysis;
};

export function SemanticAnalysisCard({ analysis }: SemanticAnalysisCardProps) {
  const confidenceColors = {
    LOW: "bg-blue-900 text-blue-200",
    MEDIUM: "bg-yellow-900 text-yellow-200",
    HIGH: "bg-orange-900 text-orange-200",
    CRITICAL: "bg-red-900 text-red-200",
  };

  return (
    <div className="space-y-4 rounded-lg border border-slate-800 bg-slate-900/80 p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-100">Semantic Analysis</h3>
          <p className="mt-1 text-sm text-slate-400">{analysis.explanation}</p>
        </div>
        <span className={`whitespace-nowrap rounded px-2.5 py-1 text-xs font-semibold ${confidenceColors[analysis.confidence]}`}>
          {analysis.confidence}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-slate-800/50 p-3">
          <p className="text-xs text-slate-500">Semantic Score</p>
          <p className="mt-1 text-lg font-semibold text-white">{(analysis.semantic_score * 100).toFixed(1)}%</p>
        </div>
        <div className="rounded bg-slate-800/50 p-3">
          <p className="text-xs text-slate-500">Threat Category</p>
          <p className="mt-1 text-sm font-semibold text-slate-200">{analysis.category}</p>
        </div>
      </div>

      <div className="rounded bg-slate-800/30 p-3">
        <p className="text-xs text-slate-500">Matched Attack Example</p>
        <p className="mt-2 text-sm text-slate-300 italic">"{analysis.matched_example}"</p>
      </div>

      {analysis.top_matches && analysis.top_matches.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400">Top Similar Threats</p>
          <div className="mt-2 space-y-2">
            {analysis.top_matches.slice(0, 3).map((match) => (
              <div key={match.threat_id} className="flex items-center justify-between rounded bg-slate-800/30 px-3 py-2 text-xs">
                <span className="flex-1 text-slate-300">{match.threat_text.substring(0, 50)}...</span>
                <span className="ml-2 whitespace-nowrap rounded bg-slate-700 px-2 py-1 font-mono text-slate-300">
                  {(match.similarity * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
