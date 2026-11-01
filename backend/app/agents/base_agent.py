from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    agent_name: str
    threat_detected: bool
    confidence: float
    score: int
    risk_level: str
    category: str
    evidence: list[str] = field(default_factory=list)
    matched_examples: list[str] = field(default_factory=list)
    recommendation: str = "ALLOW"
    processing_time: float = 0.0


class BaseSecurityAgent:
    agent_name: str = "BaseSecurityAgent"

    def analyze(self, prompt: str) -> AgentResult:
        raise NotImplementedError

    def _risk_level_for(self, score: int) -> str:
        if score <= 0:
            return "SAFE"
        if score <= 25:
            return "GOOD"
        if score <= 60:
            return "MEDIUM"
        return "HIGH"
