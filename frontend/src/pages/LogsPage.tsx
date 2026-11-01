import { Download, RefreshCw, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { DecisionBadge } from "../components/DecisionBadge";
import { EmptyState, LoadingState } from "../components/DataState";
import { useDebounce } from "../hooks/useDebounce";
import { fetchLogs } from "../services/api";
import type { PromptLog } from "../types";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function exportCsv(logs: PromptLog[]) {
  const headers = ["Time", "Prompt", "Risk Score", "Risk Level", "Decision", "Status", "User IP"];
  const rows = logs.map((log) => [
    formatDate(log.timestamp),
    log.prompt,
    String(log.risk_score),
    log.risk_level,
    log.decision,
    log.reason,
    log.user_ip,
  ]);
  const csv = [headers, ...rows]
    .map((row) => row.map((cell) => `"${cell.replaceAll('"', '""')}"`).join(","))
    .join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `prompt-logs-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

export function LogsPage() {
  const [logs, setLogs] = useState<PromptLog[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [decision, setDecision] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const debouncedSearch = useDebounce(search, 250);

  const params = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      decision: decision || undefined,
      risk_level: riskLevel || undefined,
    }),
    [debouncedSearch, decision, riskLevel],
  );

  const loadLogs = () => {
    setLoading(true);
    fetchLogs(params)
      .then((data) => {
        setLogs(data.items);
        setTotal(data.total);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadLogs();
  }, [params]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white sm:text-3xl">Prompt Logs</h1>
          <p className="mt-2 text-sm text-slate-400">{total.toLocaleString()} records</p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="relative min-w-0 sm:w-72">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={17} aria-hidden />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950 pl-10 pr-3 text-sm text-white outline-none transition focus:border-firewall-primary"
              placeholder="Search logs"
            />
          </label>
          <select
            value={decision}
            onChange={(event) => setDecision(event.target.value)}
            className="h-11 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-white outline-none transition focus:border-firewall-primary"
          >
            <option value="">All decisions</option>
            <option value="ALLOWED">Allowed</option>
            <option value="BLOCKED">Blocked</option>
          </select>
          <select
            value={riskLevel}
            onChange={(event) => setRiskLevel(event.target.value)}
            className="h-11 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-white outline-none transition focus:border-firewall-primary"
          >
            <option value="">All risk</option>
            <option value="SAFE">Safe</option>
            <option value="GOOD">Good</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>
          <button
            type="button"
            onClick={loadLogs}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 text-sm font-medium text-slate-200 transition hover:border-firewall-primary"
          >
            <RefreshCw size={17} aria-hidden />
            Refresh
          </button>
          <button
            type="button"
            onClick={() => exportCsv(logs)}
            disabled={!logs.length}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-firewall-primary px-4 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download size={17} aria-hidden />
            CSV
          </button>
        </div>
      </div>

      {loading ? <LoadingState title="Loading logs" /> : null}
      {error ? <EmptyState title="Logs unavailable" message={error} /> : null}
      {!loading && !error && !logs.length ? <EmptyState title="No logs found" /> : null}

      {!loading && !error && logs.length ? (
        <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900/80 shadow-glow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-950/70">
                <tr>
                  {["Time", "Prompt", "Risk Score", "Decision", "Status"].map((header) => (
                    <th key={header} className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40">
                    <td className="whitespace-nowrap px-4 py-4 text-sm text-slate-400">{formatDate(log.timestamp)}</td>
                    <td className="max-w-xl px-4 py-4 text-sm text-slate-200">
                      <div className="max-h-12 overflow-hidden">{log.prompt}</div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-4 text-sm font-semibold text-white">{log.risk_score}</td>
                    <td className="whitespace-nowrap px-4 py-4">
                      <DecisionBadge value={log.decision} />
                    </td>
                    <td className="min-w-52 px-4 py-4 text-sm text-slate-300">{log.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
