import type { FirewallAnalysis } from "../types";

type RiskMeterProps = {
  analysis: FirewallAnalysis | null;
};

export function RiskMeter({ analysis }: RiskMeterProps) {
  const score = analysis?.risk_score ?? 0;
  const markerPercent = score === 0 ? 0 : score <= 25 ? (score / 25) * 25 : score <= 60 ? 25 + ((score - 25) / 35) * 25 : 100;
  const levelLabel = analysis?.risk_level ?? "SAFE";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-100">Risk Score</h2>
          <p className="mt-1 text-sm text-slate-500">{levelLabel}</p>
        </div>
        <span className="text-3xl font-semibold text-white">{score}</span>
      </div>
      <div className="relative h-3 overflow-hidden rounded-full bg-slate-800">
        <div className="absolute inset-y-0 left-0 w-1/4 rounded-full bg-emerald-500/70" />
        <div className="absolute inset-y-0 left-1/4 w-1/4 rounded-full bg-sky-500/70" />
        <div className="absolute inset-y-0 left-1/2 w-1/4 rounded-full bg-amber-400/70" />
        <div className="absolute inset-y-0 left-3/4 w-1/4 rounded-full bg-red-500/70" />
        <div className="absolute inset-y-0 rounded-full bg-white/90 transition-all" style={{ width: `${Math.min(score, 100)}%` }} />
        <div className="absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full border-2 border-white bg-slate-950 shadow" style={{ left: `calc(${Math.min(markerPercent, 100)}% - 0.5rem)` }} />
      </div>
      <div className="mt-3 grid grid-cols-4 text-xs text-slate-500">
        <span>Safe</span>
        <span className="text-center">Good</span>
        <span className="text-center">Medium</span>
        <span className="text-right">High</span>
      </div>
    </div>
  );
}
