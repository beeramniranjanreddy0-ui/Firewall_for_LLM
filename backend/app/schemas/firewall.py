from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Decision = Literal["ALLOWED", "BLOCKED"]
RiskLevel = Literal["SAFE", "GOOD", "MEDIUM", "HIGH"]
Confidence = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class PromptAnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)


class FirewallDetection(BaseModel):
    rule_id: str
    category: str
    severity: str
    description: str
    match: str


class SemanticMatch(BaseModel):
    """Similar threat example from semantic search."""

    threat_id: str
    threat_text: str
    similarity: float = Field(..., ge=0, le=1)
    category: str
    rank: int


class SemanticAnalysis(BaseModel):
    """Semantic threat detection results."""

    semantic_score: float = Field(..., ge=0, le=1)
    confidence: Confidence
    category: str
    matched_example: str
    top_matches: list[SemanticMatch] = Field(default_factory=list)
    explanation: str
    is_threat: bool = Field(default=False)


class FirewallAnalysis(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    decision: Decision
    reason: str
    matched_rules: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    detections: list[FirewallDetection] = Field(default_factory=list)
    explanation: str = Field(default="Baseline rule-based analysis")
    evidence: list[str] = Field(default_factory=list)
    adaptive_updates: list[str] = Field(default_factory=list)
    baseline_only: bool = Field(default=True)
    
    # Semantic detection fields
    semantic_analysis: SemanticAnalysis | None = Field(default=None)
