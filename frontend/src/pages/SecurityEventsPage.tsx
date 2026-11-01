import { Filter, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { DecisionBadge } from "../components/DecisionBadge";
import { EmptyState, LoadingState } from "../components/DataState";
import { fetchSecurityEvents } from "../services/api";
import type { SecurityEvent } from "../types";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function eventDetails(details: string) {
  try {
    return JSON.parse(details) as { prompt_preview?: string; reason?: string; risk_score?: number };
  } catch {
    return { prompt_preview: details };
  }
}

export function SecurityEventsPage() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [severity, setSeverity] = useState("");
  const [eventType, setEventType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const params = useMemo(
    () => ({
      severity: severity || undefined,
      event_type: eventType || undefined,
    }),
    [severity, eventType],
  );

  const loadEvents = () => {
    setLoading(true);
    fetchSecurityEvents(params)
      .then((data) => {
        setEvents(data.items);
        setTotal(data.total);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvents();
  }, [params]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white sm:text-3xl">Security Events</h1>
          <p className="mt-2 text-sm text-slate-400">{total.toLocaleString()} events</p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="inline-flex h-11 items-center gap-2 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-400">
            <Filter size={16} aria-hidden />
            <select
              value={eventType}
              onChange={(event) => setEventType(event.target.value)}
              className="bg-transparent text-sm text-white outline-none"
            >
              <option value="">All event types</option>
              <option value="PROMPT_BLOCKED">Blocked prompts</option>
              <option value="JAILBREAK_DETECTED">Jailbreak attempts</option>
              <option value="PROMPT_INJECTION_DETECTED">Prompt injections</option>
            </select>
          </label>
          <select
            value={severity}
            onChange={(event) => setSeverity(event.target.value)}
            className="h-11 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-white outline-none transition focus:border-firewall-primary"
          >
            <option value="">All severity</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
          <button
            type="button"
            onClick={loadEvents}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 text-sm font-medium text-slate-200 transition hover:border-firewall-primary"
          >
            <RefreshCw size={17} aria-hidden />
            Refresh
          </button>
        </div>
      </div>

      {loading ? <LoadingState title="Loading events" /> : null}
      {error ? <EmptyState title="Events unavailable" message={error} /> : null}
      {!loading && !error && !events.length ? <EmptyState title="No security events found" /> : null}

      {!loading && !error && events.length ? (
        <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900/80 shadow-glow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-950/70">
                <tr>
                  {["Time", "Event", "Severity", "Risk", "Details"].map((header) => (
                    <th key={header} className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {events.map((event) => {
                  const details = eventDetails(event.details);
                  return (
                    <tr key={event.id} className="hover:bg-slate-800/40">
                      <td className="whitespace-nowrap px-4 py-4 text-sm text-slate-400">{formatDate(event.timestamp)}</td>
                      <td className="whitespace-nowrap px-4 py-4 text-sm font-semibold text-slate-100">{event.event_type}</td>
                      <td className="whitespace-nowrap px-4 py-4">
                        <DecisionBadge value={event.severity} />
                      </td>
                      <td className="whitespace-nowrap px-4 py-4 text-sm font-semibold text-white">{details.risk_score ?? "-"}</td>
                      <td className="max-w-2xl px-4 py-4 text-sm text-slate-300">
                        <div className="max-h-16 overflow-hidden">
                          {details.reason ? <span className="font-medium text-slate-100">{details.reason}: </span> : null}
                          {details.prompt_preview}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
