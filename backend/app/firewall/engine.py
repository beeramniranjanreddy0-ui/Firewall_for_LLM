from __future__ import annotations

from app.firewall.agents import RiskAgent, RuleAgent, SemanticAgent
from app.firewall.decision import DecisionEngine
from app.firewall.detectors import FirewallDetector
from app.firewall.scoring import RiskScorer
from app.schemas.firewall import (
    FirewallAnalysis,
    FirewallDetection,
    SemanticAnalysis,
    SemanticMatch,
)


class FirewallEngine:
    def __init__(
        self,
        detector: FirewallDetector | None = None,
        scorer: RiskScorer | None = None,
        decision_engine: DecisionEngine | None = None,
    ) -> None:
        self.detector = detector or FirewallDetector()
        self.scorer = scorer or RiskScorer()
        self.decision_engine = decision_engine or DecisionEngine()
        self.rule_agent = RuleAgent(detector=self.detector)
        self.semantic_agent = SemanticAgent()
        self.risk_agent = RiskAgent(scorer=self.scorer, decision_engine=self.decision_engine)
        self.adaptive_rules: list[str] = []

    def analyze(self, prompt: str) -> FirewallAnalysis:
        baseline_detections = self.rule_agent.analyze(prompt)
        semantic_detections, semantic_context = self.semantic_agent.analyze(prompt)
        risk_score, risk_level, decision, explanation_parts, evidence = self.risk_agent.analyze(
            prompt,
            baseline_detections,
            semantic_detections,
            semantic_context,
        )

        detections = [*baseline_detections, *semantic_detections]
        explanation = " | ".join(explanation_parts)
        baseline_only = not semantic_detections

        # Build semantic analysis if available
        semantic_analysis = None
        if semantic_context.get("is_semantic_threat"):
            top_matches = semantic_context.get("top_matches", [])
            semantic_analysis = SemanticAnalysis(
                semantic_score=semantic_context.get("semantic_similarity", 0.0),
                confidence=semantic_context.get("confidence", "LOW"),
                category=semantic_context.get("category", "Unknown"),
                matched_example=semantic_context.get("matched_example", ""),
                top_matches=[
                    SemanticMatch(
                        threat_id=match.get("threat_id", ""),
                        threat_text=match.get("threat_text", ""),
                        similarity=match.get("similarity", 0.0),
                        category=match.get("category", ""),
                        rank=match.get("rank", 0),
                    )
                    for match in top_matches
                ],
                explanation=semantic_context.get("explanation", ""),
                is_threat=semantic_context.get("is_threat", False),
            )

        return FirewallAnalysis(
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            reason=self._reason_for(decision, detections, semantic_context),
            matched_rules=[item.rule_id for item in detections],
            categories=sorted({item.category for item in detections}),
            detections=[
                FirewallDetection(
                    rule_id=item.rule_id,
                    category=item.category,
                    severity=item.severity,
                    description=item.description,
                    match=item.match,
                )
                for item in detections
            ],
            explanation=explanation,
            evidence=evidence,
            adaptive_updates=self.adaptive_rules,
            baseline_only=baseline_only,
            semantic_analysis=semantic_analysis,
        )

    def apply_adaptive_updates(self, analysis: FirewallAnalysis) -> int:
        if analysis.decision == "BLOCKED" and not analysis.baseline_only:
            self.adaptive_rules.append(
                f"semantic:{analysis.reason.lower().replace(' ', '_')}"
            )
            return len(self.adaptive_rules)
        return len(self.adaptive_rules)

    @staticmethod
    def _reason_for(decision: str, detections: list[object], semantic_context: dict[str, object]) -> str:
        if decision == "BLOCKED":
            return "Prompt blocked by multi-agent firewall"
        if semantic_context.get("suspicious_terms"):
            return "Prompt flagged for suspicious language"
        return "Prompt Allowed"
