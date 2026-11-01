import type { LucideIcon } from "lucide-react";

type StatCardProps = {
  title: string;
  value: number;
  icon: LucideIcon;
  tone: "primary" | "success" | "danger" | "warning";
};

const toneClasses = {
  primary: "bg-firewall-primary/15 text-blue-300",
  success: "bg-firewall-success/15 text-emerald-300",
  danger: "bg-firewall-danger/15 text-red-300",
  warning: "bg-amber-400/15 text-amber-200",
};

export function StatCard({ title, value, icon: Icon, tone }: StatCardProps) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-slate-400">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-white">{value.toLocaleString()}</p>
        </div>
        <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${toneClasses[tone]}`}>
          <Icon size={22} aria-hidden />
        </div>
      </div>
    </div>
  );
}
