from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.semantic.faiss_index import FAISSIndex
from app.semantic.similarity import confidence_level


@dataclass
class SemanticResult:
    is_threat: bool
    semantic_score: float
    confidence: str
    category: str
    matched_example: str
    top_matches: list[dict[str, Any]]
    explanation: str
    normalized_category: str


class SemanticDetector:
    def __init__(self, semantic_threshold: float = 0.70, top_k: int = 5) -> None:
        self.semantic_threshold = semantic_threshold
        self.top_k = top_k
        self.index = FAISSIndex(top_k=top_k, similarity_threshold=0.0)

    def detect(self, prompt: str) -> SemanticResult:
        if not isinstance(prompt, str) or not prompt.strip():
            return self._make_result(
                is_threat=False,
                semantic_score=0.0,
                confidence="LOW",
                category="Unknown",
                matched_example="",
                top_matches=[],
                explanation="No content to analyze.",
                normalized_category="semantic_threat",
            )

        matches = self.index.search_similar(prompt, similarity_threshold=0.0, top_k=self.top_k)
        best_match = matches[0] if matches else None
        semantic_score = float(best_match["similarity"]) if best_match else 0.0
        confidence = confidence_level(semantic_score)
        category = self._resolve_category(matches, best_match)
        normalized_category = self._normalize_category(category)
        matched_example = best_match["threat_text"] if best_match else ""

        category_thresholds = {
            "Prompt Injection": 0.60,
            "Jailbreak": 0.58,
            "Instruction Override": 0.50,
            "Sensitive Data Leakage": 0.65,
            "Role Manipulation": 0.65,
            "Prompt Extraction": 0.75,
        }
        category_threshold = category_thresholds.get(category, self.semantic_threshold)
        is_threat = semantic_score >= category_threshold

        if confidence == "CRITICAL" and semantic_score >= 0.80:
            is_threat = True

        attack_keywords = {
            "ignore",
            "previous",
            "instructions",
            "prompt",
            "system",
            "bypass",
            "restrictions",
            "jailbreak",
            "disregard",
            "follow",
            "new",
            "unrestricted",
            "assistant",
            "forget",
            "stop",
            "pretend",
            "secret",
            "reveal",
            "password",
            "confidential",
            "data",
            "leak",
            "attack",
        }
        prompt_tokens = {token for token in prompt.lower().split() if token}
        if prompt_tokens & attack_keywords:
            if category in {"Prompt Injection", "Jailbreak", "Instruction Override", "Sensitive Data Leakage"}:
                is_threat = True
            elif semantic_score >= 0.35:
                is_threat = True

        high_risk_categories = {
            "Prompt Injection",
            "Jailbreak",
            "Prompt Extraction",
            "Sensitive Data Leakage",
            "Role Manipulation",
            "Instruction Override",
        }

        high_risk_matches = [m for m in matches if m.get("category") in high_risk_categories]
        if category in high_risk_categories and len(high_risk_matches) >= 2 and semantic_score >= 0.60:
            is_threat = True

        if category in high_risk_categories and len(high_risk_matches) >= 3 and semantic_score >= 0.65:
            is_threat = True

        explanation = (
            f"Semantic threat matched {category} example with score {semantic_score:.3f}."
            if is_threat
            else f"No semantic threat detected above threshold {self.semantic_threshold:.2f}."
        )

        return self._make_result(
            is_threat=is_threat,
            semantic_score=semantic_score,
            confidence=confidence,
            category=category,
            matched_example=matched_example,
            top_matches=matches,
            explanation=explanation,
            normalized_category=normalized_category,
        )

    def detect_batch(self, prompts: list[str]) -> list[SemanticResult]:
        return [self.detect(prompt) for prompt in prompts]

    def update_threshold(self, threshold: float) -> None:
        if 0.0 < threshold < 1.0:
            self.semantic_threshold = threshold

    def get_stats(self) -> dict[str, Any]:
        return {
            "threshold": self.semantic_threshold,
            "top_k": self.top_k,
            "index_stats": self.index.get_index_stats(),
            "categories": self.index.db.get_categories(),
        }

    def _resolve_category(self, matches: list[dict[str, Any]], best_match: dict[str, Any] | None) -> str:
        if not best_match:
            return "Unknown"

        categories = [match.get("category", "Unknown") for match in matches]
        high_risk_categories = [
            category
            for category in categories
            if category in {
                "Prompt Injection",
                "Jailbreak",
                "Prompt Extraction",
                "Sensitive Data Leakage",
                "Role Manipulation",
                "Instruction Override",
            }
        ]

        if high_risk_categories:
            return max(set(high_risk_categories), key=high_risk_categories.count)

        return best_match.get("category", "Unknown")

    def _normalize_category(self, category: str) -> str:
        normalized = category.lower().replace(" ", "_").replace("-", "_")
        return normalized

    def _make_result(
        self,
        is_threat: bool,
        semantic_score: float,
        confidence: str,
        category: str,
        matched_example: str,
        top_matches: list[dict[str, Any]],
        explanation: str,
        normalized_category: str,
    ) -> SemanticResult:
        return SemanticResult(
            is_threat=is_threat,
            semantic_score=semantic_score,
            confidence=confidence,
            category=category,
            matched_example=matched_example,
            top_matches=top_matches,
            explanation=explanation,
            normalized_category=normalized_category,
        )
