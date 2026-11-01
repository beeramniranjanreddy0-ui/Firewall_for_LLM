import axios from "axios";

import type {
  ChatRequest,
  ChatResponse,
  FirewallAnalysis,
  FirewallStats,
  ListResponse,
  PromptLog,
  SecurityEvent,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 70000,
  headers: {
    "Content-Type": "application/json",
  },
});

function apiError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return new Error(detail);
    }
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (typeof item?.msg === "string") {
            return item.msg;
          }
          return null;
        })
        .filter(Boolean);

      if (messages.length) {
        return new Error(messages.join("; "));
      }
    }
    return new Error(error.message);
  }
  return error instanceof Error ? error : new Error("Unexpected API error");
}

export async function analyzePrompt(prompt: string): Promise<FirewallAnalysis> {
  try {
    const response = await client.post<FirewallAnalysis>("/api/firewall/analyze", { prompt });
    return response.data;
  } catch (error) {
    throw apiError(error);
  }
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await client.post<ChatResponse>("/api/chat", payload);
    return response.data;
  } catch (error) {
    throw apiError(error);
  }
}

export async function fetchLogs(params?: Record<string, string | undefined>): Promise<ListResponse<PromptLog>> {
  try {
    const response = await client.get<ListResponse<PromptLog>>("/api/logs", { params });
    return response.data;
  } catch (error) {
    throw apiError(error);
  }
}

export async function fetchSecurityEvents(params?: Record<string, string | undefined>): Promise<ListResponse<SecurityEvent>> {
  try {
    const response = await client.get<ListResponse<SecurityEvent>>("/api/security-events", { params });
    return response.data;
  } catch (error) {
    throw apiError(error);
  }
}

export async function fetchStats(): Promise<FirewallStats> {
  try {
    const response = await client.get<FirewallStats>("/api/stats");
    return response.data;
  } catch (error) {
    throw apiError(error);
  }
}
