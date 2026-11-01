from __future__ import annotations

import time

from app.agents.base_agent import AgentResult, BaseSecurityAgent


class JailbreakAgent(BaseSecurityAgent):
    agent_name = "JailbreakAgent"

    def analyze(self, prompt: str) -> AgentResult:
        started = time.perf_counter()
        lowered = prompt.lower()
        patterns = [
            "jailbreak",
            "dan mode",
            "developer mode",
            "ignore safety",
            "bypass",
            "unrestricted",
            "disable restrictions",
        ]
        matched = [item for item in patterns if item in lowered]
        score = min(20 * len(matched), 100)
        threat_detected = score >= 35
        evidence = [f"Matched jailbreak pattern: {item}" for item in matched] or ["No jailbreak-like phrasing detected"]
        return AgentResult(
            agent_name=self.agent_name,
            threat_detected=threat_detected,
            confidence=min(0.99, 0.5 + (len(matched) / len(patterns)) * 0.45),
            score=score,
            risk_level=self._risk_level_for(score),
            category="jailbreak",
            evidence=evidence,
            matched_examples=matched,
            recommendation="BLOCK" if threat_detected else "ALLOW",
            processing_time=time.perf_counter() - started,
        )
