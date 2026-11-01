from __future__ import annotations

import time

from app.agents.base_agent import AgentResult, BaseSecurityAgent


class PrivacyAgent(BaseSecurityAgent):
    agent_name = "PrivacyAgent"

    def analyze(self, prompt: str) -> AgentResult:
        started = time.perf_counter()
        lowered = prompt.lower()
        secrets = [
            "api key",
            "password",
            "secret",
            "system prompt",
            "internal instructions",
            "database",
            "conversation history",
            "personal information",
        ]
        matched = [item for item in secrets if item in lowered]
        score = min(30 * len(matched), 100)
        threat_detected = score >= 35
        evidence = [f"Requested sensitive data: {item}" for item in matched] or ["No privacy request patterns detected"]
        return AgentResult(
            agent_name=self.agent_name,
            threat_detected=threat_detected,
            confidence=min(0.99, 0.45 + (len(matched) / len(secrets)) * 0.5),
            score=score,
            risk_level=self._risk_level_for(score),
            category="privacy",
            evidence=evidence,
            matched_examples=matched,
            recommendation="BLOCK" if threat_detected else "ALLOW",
            processing_time=time.perf_counter() - started,
        )
