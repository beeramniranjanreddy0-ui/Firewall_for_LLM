from __future__ import annotations

import time

from app.agents.base_agent import AgentResult, BaseSecurityAgent
from app.firewall.detectors import FirewallDetector


class PromptInjectionAgent(BaseSecurityAgent):
    agent_name = "PromptInjectionAgent"

    def __init__(self, detector: FirewallDetector | None = None, semantic_detector: object | None = None) -> None:
        self.detector = detector or FirewallDetector()
        self.semantic_detector = semantic_detector
        if self.semantic_detector is None:
            try:
                from app.semantic.semantic_detector import SemanticDetector

                self.semantic_detector = SemanticDetector()
            except Exception:
                self.semantic_detector = None

    def analyze(self, prompt: str) -> AgentResult:
        started = time.perf_counter()
        detections = [item for item in self.detector.detect(prompt) if item.category in {"prompt_injection", "prompt_extraction", "instruction_override", "role_manipulation"}]
        semantic_result = None
        if self.semantic_detector is not None:
            try:
                semantic_result = self.semantic_detector.detect(prompt)
            except Exception:
                semantic_result = None
        score = 0
        evidence: list[str] = []
        if detections:
            score += 45
            evidence.extend(item.description for item in detections[:3])
        if semantic_result is not None and semantic_result.is_threat and semantic_result.semantic_score >= 0.6:
            score += 35
            evidence.append(semantic_result.explanation)
        if "ignore" in prompt.lower() or "system prompt" in prompt.lower():
            score += 15
            evidence.append("Prompt contains override-style language")
        score = min(score, 100)
        threat_detected = score >= 40
        return AgentResult(
            agent_name=self.agent_name,
            threat_detected=threat_detected,
            confidence=min(0.99, 0.55 + (score / 100) * 0.4),
            score=score,
            risk_level=self._risk_level_for(score),
            category="prompt_injection",
            evidence=evidence or ["No strong prompt injection signals detected"],
            matched_examples=[semantic_result.matched_example] if semantic_result is not None and semantic_result.matched_example else [],
            recommendation="BLOCK" if threat_detected else "ALLOW",
            processing_time=time.perf_counter() - started,
        )
