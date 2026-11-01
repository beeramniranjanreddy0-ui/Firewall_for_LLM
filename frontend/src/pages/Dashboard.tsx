import { AlertTriangle, CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";

import { DecisionBreakdownChart, RecentActivityChart, RiskDistributionChart } from "../components/Charts";
import { EmptyState, LoadingState } from "../components/DataState";
import { StatCard } from "../components/StatCard";
import { useFirewallStats } from "../hooks/useFirewallStats";

export function Dashboard() {
  const { stats, loading, error } = useFirewallStats();

  if (loading) {
    return <LoadingState title="Loading dashboard" />;
  }

  if (error || !stats) {
    return <EmptyState title="Dashboard unavailable" message={error ?? "Backend API did not return stats."} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white sm:text-3xl">Security Dashboard</h1>
          <p className="mt-2 text-sm text-slate-400">AI firewall traffic, decisions, and risk posture.</p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-300">
          Events: <span className="font-semibold text-white">{stats.total_security_events.toLocaleString()}</span>
        </div>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Prompts" value={stats.total_prompts} icon={ShieldCheck} tone="primary" />
        <StatCard title="Allowed Prompts" value={stats.allowed_prompts} icon={CheckCircle2} tone="success" />
        <StatCard title="Blocked Prompts" value={stats.blocked_prompts} icon={ShieldAlert} tone="danger" />
        <StatCard title="High Risk Prompts" value={stats.high_risk_prompts} icon={AlertTriangle} tone="warning" />
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <DecisionBreakdownChart allowed={stats.allowed_prompts} blocked={stats.blocked_prompts} />
        <RiskDistributionChart data={stats.risk_distribution} />
        <RecentActivityChart data={stats.recent_activity} />
      </section>
    </div>
  );
}
