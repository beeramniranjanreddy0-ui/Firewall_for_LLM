from __future__ import annotations

from app.agents.base_agent import AgentResult


class RiskEngine:
    def __init__(self) -> None:
        self.weights = {
            "rule": 0.15,
            "semantic": 0.25,
            "injection": 0.20,
            "jailbreak": 0.15,
            "privacy": 0.15,
            "toxicity": 0.10,
        }

    def evaluate(
        self,
        *,
        rule_score: int,
        semantic_score: float,
        injection_score: int,
        jailbreak_score: int,
        privacy_score: int,
        toxicity_score: int,
    ) -> dict[str, object]:
        normalized_semantic = min(max(float(semantic_score) * 100, 0), 100)
        final_score = (
            self.weights["rule"] * rule_score
            + self.weights["semantic"] * normalized_semantic
            + self.weights["injection"] * injection_score
            + self.weights["jailbreak"] * jailbreak_score
            + self.weights["privacy"] * privacy_score
            + self.weights["toxicity"] * toxicity_score
        )
        final_score = round(min(max(final_score, 0), 100), 2)
        if final_score <= 25:
            risk_level = "SAFE"
            decision = "ALLOW"
        elif final_score <= 50:
            risk_level = "GOOD"
            decision = "WARN"
        elif final_score <= 75:
            risk_level = "MEDIUM"
            decision = "REQUIRE REVIEW"
        else:
            risk_level = "HIGH"
            decision = "BLOCK"
        return {
            "final_score": final_score,
            "risk_level": risk_level,
            "decision": decision,
        }
