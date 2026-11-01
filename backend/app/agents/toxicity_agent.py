from __future__ import annotations

import time

from app.agents.base_agent import AgentResult, BaseSecurityAgent


class ToxicityAgent(BaseSecurityAgent):
    agent_name = "ToxicityAgent"

    def analyze(self, prompt: str) -> AgentResult:
        started = time.perf_counter()
        lowered = prompt.lower()
        toxic_terms = [
            "hate",
            "worthless",
            "idiot",
            "stupid",
            "kill",
            "violence",
            "self harm",
            "illegal",
            "abuse",
        ]
        matched = [item for item in toxic_terms if item in lowered]
        score = min(15 * len(matched), 100)
        threat_detected = score >= 25
        evidence = [f"Matched toxicity term: {item}" for item in matched] or ["No toxic language detected"]
        return AgentResult(
            agent_name=self.agent_name,
            threat_detected=threat_detected,
            confidence=min(0.99, 0.45 + (len(matched) / len(toxic_terms)) * 0.5),
            score=score,
            risk_level=self._risk_level_for(score),
            category="toxicity",
            evidence=evidence,
            matched_examples=matched,
            recommendation="WARN" if threat_detected else "ALLOW",
            processing_time=time.perf_counter() - started,
        )
