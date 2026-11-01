import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { RecentActivity, RiskDistribution } from "../types";

type RiskDistributionChartProps = {
  data: RiskDistribution;
};

type DecisionBreakdownChartProps = {
  allowed: number;
  blocked: number;
};

type RecentActivityChartProps = {
  data: RecentActivity[];
};

const riskItems = [
  { key: "SAFE", label: "Safe", color: "#22c55e" },
  { key: "GOOD", label: "Good", color: "#38bdf8" },
  { key: "MEDIUM", label: "Medium", color: "#f59e0b" },
  { key: "HIGH", label: "High", color: "#ef4444" },
] as const;

function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-100">{title}</h2>
          {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
        </div>
      </div>
      <div className="h-72 w-full">{children}</div>
    </div>
  );
}

export function DecisionBreakdownChart({ allowed, blocked }: DecisionBreakdownChartProps) {
  const data = [
    { name: "Allowed", value: allowed, fill: "#22c55e" },
    { name: "Blocked", value: blocked, fill: "#ef4444" },
  ];

  return (
    <ChartCard title="Allowed vs Blocked" subtitle="Prompt decisions over time">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
          <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <Tooltip cursor={{ fill: "rgba(148, 163, 184, 0.08)" }} />
          <Bar dataKey="value" radius={[8, 8, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function RiskDistributionChart({ data }: RiskDistributionChartProps) {
  const chartData = riskItems.map((item) => ({ ...item, value: data[item.key] }));

  return (
    <ChartCard title="Risk Distribution" subtitle="Current exposure breakdown">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="label" innerRadius={70} outerRadius={110} paddingAngle={2}>
            {chartData.map((entry) => (
              <Cell key={entry.key} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function RecentActivityChart({ data }: RecentActivityChartProps) {
  return (
    <ChartCard title="Recent Security Events" subtitle="Daily prompt volume and blocked events">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
          <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={3} dot={{ r: 3, fill: "#3b82f6" }} />
          <Line type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={3} dot={{ r: 3, fill: "#ef4444" }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
