import type { Decision, RiskLevel, Severity } from "../types";

type DecisionBadgeProps = {
  value: Decision | RiskLevel | Severity | string;
};

export function DecisionBadge({ value }: DecisionBadgeProps) {
  const normalized = value.toUpperCase();
  const className =
    normalized === "ALLOWED" || normalized === "SAFE" || normalized === "LOW"
      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
      : normalized === "GOOD"
        ? "border-sky-500/30 bg-sky-500/10 text-sky-200"
        : normalized === "MEDIUM"
          ? "border-amber-400/30 bg-amber-400/10 text-amber-200"
          : normalized === "BLOCKED" || normalized === "HIGH" || normalized === "CRITICAL"
            ? "border-red-500/30 bg-red-500/10 text-red-300"
            : "border-slate-600 bg-slate-800 text-slate-300";

  return (
    <span className={`inline-flex min-w-20 items-center justify-center rounded-md border px-2.5 py-1 text-xs font-semibold ${className}`}>
      {value}
    </span>
  );
}
