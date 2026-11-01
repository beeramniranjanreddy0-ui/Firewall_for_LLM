import { AlertTriangle, BrainCircuit, Play, ShieldCheck } from "lucide-react";
import { useState } from "react";

import { DecisionBadge } from "../components/DecisionBadge";
import { EmptyState } from "../components/DataState";
import { RiskMeter } from "../components/RiskMeter";
import { SemanticAnalysisCard } from "../components/SemanticAnalysisCard";
import { analyzePrompt, sendChat } from "../services/api";
import type { ChatResponse, FirewallAnalysis, LLMProviderName } from "../types";

const providerOptions: { label: string; value: LLMProviderName }[] = [
  { label: "Ollama", value: "ollama" },
  { label: "OpenAI", value: "openai" },
  { label: "Gemini", value: "gemini" },
];

export function PromptTestingPage() {
  const [prompt, setPrompt] = useState("");
  const [provider, setProvider] = useState<LLMProviderName>("ollama");
  const [analysis, setAnalysis] = useState<FirewallAnalysis | null>(null);
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState<"analyze" | "send" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isDisabled = !prompt.trim() || Boolean(loading);

  const handleAnalyze = async () => {
    setLoading("analyze");
    setError(null);
    setChatResponse(null);
    try {
      const result = await analyzePrompt(prompt);
      setAnalysis(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(null);
    }
  };

  const handleSend = async () => {
    setLoading("send");
    setError(null);
    try {
      const result = await sendChat({ prompt, provider });
      setAnalysis(result.analysis);
      setChatResponse(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white sm:text-3xl">Prompt Testing</h1>
        <p className="mt-2 text-sm text-slate-400">User prompt to firewall to LLM to firewall to user.</p>
      </div>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <label htmlFor="prompt" className="text-base font-semibold text-slate-100">
              Prompt Input
            </label>
            <select
              value={provider}
              onChange={(event) => setProvider(event.target.value as LLMProviderName)}
              className="h-10 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-white outline-none transition focus:border-firewall-primary"
            >
              {providerOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="min-h-72 w-full resize-y rounded-lg border border-slate-700 bg-slate-950 p-4 text-sm leading-6 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-firewall-primary"
            placeholder="Explain machine learning"
            maxLength={8000}
          />
          <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span className="text-sm text-slate-500">{prompt.length.toLocaleString()} / 8,000</span>
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={isDisabled}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-950 px-4 text-sm font-medium text-slate-100 transition hover:border-firewall-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ShieldCheck size={17} aria-hidden />
                {loading === "analyze" ? "Analyzing" : "Analyze"}
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={isDisabled}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-firewall-primary px-4 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Play size={17} aria-hidden />
                {loading === "send" ? "Sending" : "Send to LLM"}
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <RiskMeter analysis={analysis} />
          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-slate-100">Firewall Decision</h2>
              {analysis ? <DecisionBadge value={analysis.decision} /> : null}
            </div>
            {analysis ? (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-500">Reason</p>
                  <p className="mt-1 text-sm font-medium text-slate-100">{analysis.reason}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Risk Level</p>
                  <p className="mt-1 text-sm font-medium text-slate-100">{analysis.risk_level}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Matched Rules</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {analysis.matched_rules.length ? (
                      analysis.matched_rules.map((rule) => (
                        <span key={rule} className="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-300">
                          {rule}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400">None</span>
                    )}
                  </div>
                </div>
                {analysis.detections?.length ? (
                  <div>
                    <p className="text-sm text-slate-500">Detections</p>
                    <div className="mt-2 space-y-2">
                      {analysis.detections.map((detection) => (
                        <div key={detection.rule_id} className="rounded-lg border border-slate-800 bg-slate-950 p-3">
                          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                            <p className="text-sm font-medium text-slate-100">{detection.rule_id}</p>
                            <span className="w-fit rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-300">
                              {detection.severity}
                            </span>
                          </div>
                          <p className="mt-2 text-sm text-slate-400">{detection.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
                {analysis.semantic_analysis ? (
                  <div>
                    <p className="text-sm text-slate-500">Semantic Threat Detection</p>
                    <div className="mt-2">
                      <SemanticAnalysisCard analysis={analysis.semantic_analysis} />
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
              <EmptyState title="No decision yet" />
            )}
          </div>
        </div>
      </section>

      {error ? <EmptyState title="Request failed" message={error} /> : null}

      <section className="rounded-lg border border-slate-800 bg-slate-900/80 p-5 shadow-glow">
        <div className="mb-4 flex items-center gap-2">
          {chatResponse?.status === "PROVIDER_ERROR" ? (
            <AlertTriangle className="text-amber-300" size={19} aria-hidden />
          ) : (
            <BrainCircuit className="text-firewall-primary" size={19} aria-hidden />
          )}
          <h2 className="text-base font-semibold text-slate-100">LLM Response</h2>
        </div>
        {chatResponse?.status === "PROVIDER_ERROR" ? (
          <div className="rounded-lg border border-amber-400/30 bg-amber-400/10 p-4 text-sm leading-6 text-amber-100">
            {chatResponse.error}
          </div>
        ) : chatResponse ? (
          <div className="whitespace-pre-wrap rounded-lg border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-100">
            {chatResponse.response || "No response content returned by provider."}
          </div>
        ) : (
          <EmptyState title="No response yet" />
        )}
      </section>
    </div>
  );
}
