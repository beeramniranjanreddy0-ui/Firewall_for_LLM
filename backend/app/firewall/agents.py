from __future__ import annotations

from typing import Any

from app.firewall.decision import DecisionEngine
from app.firewall.detectors import Detection, FirewallDetector
from app.firewall.scoring import RiskScorer
from app.semantic.semantic_detector import SemanticDetector


class RuleAgent:
    def __init__(self, detector: FirewallDetector | None = None) -> None:
        self.detector = detector or FirewallDetector()

    def analyze(self, prompt: str) -> list[Detection]:
        return self.detector.detect(prompt)


class SemanticAgent:
    def __init__(self, semantic_detector: SemanticDetector | None = None) -> None:
        """
        Initialize semantic agent with semantic detector.

        Args:
            semantic_detector: SemanticDetector instance for threat detection
        """
        self.detector = semantic_detector or SemanticDetector()

    def analyze(self, prompt: str) -> tuple[list[Detection], dict[str, Any]]:
        """
        Analyze prompt using semantic threat detection.

        Args:
            prompt: Prompt to analyze

        Returns:
            Tuple of (detections, semantic_context)
        """
        result = self.detector.detect(prompt)

        # Convert semantic result to Detection objects
        detections: list[Detection] = []

        if result.is_threat:
            category = self._normalize_category(result.category)
            detections.append(
                Detection(
                    rule_id="semantic.transformer_similarity",
                    category=category,
                    severity="HIGH",
                    description=result.explanation,
                    match=prompt[:120],
                )
            )

        normalized_category = self._normalize_category(result.category)
        semantic_context = {
            "semantic_similarity": result.semantic_score,
            "confidence": result.confidence,
            "category": result.category,
            "normalized_category": normalized_category,
            "matched_example": result.matched_example,
            "top_matches": result.top_matches,
            "is_semantic_threat": result.is_threat,
            "is_threat": result.is_threat,
        }

        return detections, semantic_context

    @staticmethod
    def _normalize_category(category: str) -> str:
        mapping = {
            "Prompt Injection": "prompt_injection",
            "Jailbreak": "jailbreak",
            "Prompt Extraction": "prompt_extraction",
            "Sensitive Data Leakage": "sensitive_data_leakage",
            "Unknown": "semantic_threat",
        }
        return mapping.get(category, category.lower().replace(" ", "_") if category else "semantic_threat")


class RiskAgent:
    def __init__(self, scorer: RiskScorer | None = None, decision_engine: DecisionEngine | None = None) -> None:
        self.scorer = scorer or RiskScorer()
        self.decision_engine = decision_engine or DecisionEngine()

    def analyze(
        self,
        prompt: str,
        baseline_detections: list[Detection],
        semantic_detections: list[Detection],
        semantic_context: dict[str, Any],
    ) -> tuple[int, str, str, list[str], list[Detection]]:
        all_detections = [*baseline_detections, *semantic_detections]
        baseline_score = self.scorer.score(baseline_detections)
        semantic_boost = 0

        # Calculate semantic boost based on detection results
        if semantic_detections:
            semantic_similarity = semantic_context.get("semantic_similarity", 0.0)
            confidence = semantic_context.get("confidence", "LOW")

            # Boost based on similarity score
            if semantic_similarity >= 0.85:
                semantic_boost += 70
            elif semantic_similarity >= 0.75:
                semantic_boost += 60
            elif semantic_similarity >= 0.65:
                semantic_boost += 50
            elif semantic_similarity >= 0.55:
                semantic_boost += 35
            elif semantic_similarity >= 0.35:
                semantic_boost += 25

            # Confidence bonus
            if confidence == "CRITICAL":
                semantic_boost += 20
            elif confidence == "HIGH":
                semantic_boost += 15
            elif confidence == "MEDIUM":
                semantic_boost += 10

            # Additional boost for strong semantic categories
            normalized_category = semantic_context.get("normalized_category", "")
            strong_semantic_categories = {
                "prompt_injection",
                "jailbreak",
                "prompt_extraction",
                "sensitive_data_leakage",
                "role_manipulation",
                "instruction_override",
            }
            if normalized_category in strong_semantic_categories:
                if semantic_similarity >= 0.70:
                    semantic_boost += 80
                elif semantic_similarity >= 0.60:
                    semantic_boost += 70
                elif semantic_similarity >= 0.50:
                    semantic_boost += 65
                elif semantic_similarity >= 0.45:
                    semantic_boost += 50
                elif semantic_similarity >= 0.35:
                    semantic_boost += 40

        # Combined detection multiplier
        if len(all_detections) >= 2:
            semantic_boost += 10
        if len(all_detections) >= 3:
            semantic_boost += 10

        risk_score = min(baseline_score + semantic_boost, 100)
        decision, reason = self.decision_engine.decide(risk_score, all_detections)

        if decision == "BLOCKED" and semantic_boost:
            reason = "Semantic attack pattern detected using transformer embeddings"

        explanation_parts = ["Baseline: no classical rule matches were found."]
        if baseline_detections:
            explanation_parts = [
                f"Baseline: rule-based engine matched {', '.join(sorted({item.rule_id for item in baseline_detections}))}."
            ]
        if semantic_detections:
            semantic_score = semantic_context.get("semantic_similarity", 0.0)
            category = semantic_context.get("category", "Unknown")
            explanation_parts.append(
                f"Semantic engine detected {category.lower()} threat "
                f"(similarity: {semantic_score:.3f}, confidence: {semantic_context.get('confidence', 'LOW')})."
            )

        evidence = [item.description for item in all_detections]
        return risk_score, self.scorer.level(risk_score), decision, explanation_parts, evidence
