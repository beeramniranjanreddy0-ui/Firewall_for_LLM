export type Decision = "ALLOWED" | "BLOCKED";
export type RiskLevel = "SAFE" | "GOOD" | "MEDIUM" | "HIGH";
export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type Confidence = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type LLMProviderName = "ollama" | "openai" | "gemini";
export type ChatStatus = "COMPLETED" | "BLOCKED" | "PROVIDER_ERROR";

export type FirewallDetection = {
  rule_id: string;
  category: string;
  severity: string;
  description: string;
  match: string;
};

export type SemanticMatch = {
  threat_id: string;
  threat_text: string;
  similarity: number;
  category: string;
  rank: number;
};

export type SemanticAnalysis = {
  semantic_score: number;
  confidence: Confidence;
  category: string;
  matched_example: string;
  top_matches: SemanticMatch[];
  explanation: string;
};

export type FirewallAnalysis = {
  risk_score: number;
  risk_level: RiskLevel;
  decision: Decision;
  reason: string;
  matched_rules: string[];
  categories: string[];
  detections?: FirewallDetection[];
  explanation?: string;
  evidence?: string[];
  semantic_analysis?: SemanticAnalysis;
};

export type ChatRequest = {
  prompt: string;
  provider?: LLMProviderName;
};

export type ChatResponse = {
  prompt: string;
  response: string;
  analysis: FirewallAnalysis;
  provider: string;
  status: ChatStatus;
  error: string | null;
  log_id: number | null;
};

export type PromptLog = {
  id: number;
  timestamp: string;
  prompt: string;
  response: string | null;
  risk_score: number;
  risk_level: RiskLevel;
  decision: Decision;
  user_ip: string;
  reason: string;
  semantic_score?: number;
  semantic_category?: string;
  matched_attack?: string;
  similarity?: number;
  confidence?: Confidence;
};

export type SecurityEvent = {
  id: number;
  timestamp: string;
  event_type: string;
  severity: Severity;
  details: string;
};

export type ListResponse<T> = {
  total: number;
  items: T[];
};

export type RiskDistribution = {
  SAFE: number;
  GOOD: number;
  MEDIUM: number;
  HIGH: number;
};

export type RecentActivity = {
  date: string;
  total: number;
  blocked: number;
};

export type FirewallStats = {
  total_prompts: number;
  allowed_prompts: number;
  blocked_prompts: number;
  high_risk_prompts: number;
  total_security_events: number;
  risk_distribution: RiskDistribution;
  recent_activity: RecentActivity[];
};
