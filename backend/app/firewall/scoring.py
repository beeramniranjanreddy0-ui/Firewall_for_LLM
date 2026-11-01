from __future__ import annotations

from app.firewall.detectors import Detection


class RiskScorer:
    def score(self, detections: list[Detection]) -> int:
        score = 0

        keyword_detections = [item for item in detections if item.rule_id.startswith(("keyword.", "jailbreak."))]
        prompt_injection_patterns = [
            item for item in detections if item.category == "prompt_injection" and item.rule_id.startswith("pattern.")
        ]
        jailbreak_patterns = [
            item for item in detections if item.category == "jailbreak" and item.rule_id.startswith("pattern.")
        ]

        if detections:
            score += min(12 * len(detections), 36)

        if keyword_detections:
            score += 20 if len(keyword_detections) == 1 else 40
            if any(item.category in {"prompt_injection", "jailbreak"} for item in keyword_detections):
                score = max(score, 60)

        if prompt_injection_patterns:
            score += 60

        if jailbreak_patterns:
            score += 60

        if any(item.rule_id == "length.very_long_prompt" for item in detections):
            score += 25
        elif any(item.rule_id == "length.long_prompt" for item in detections):
            score += 15

        return min(score, 100)

    @staticmethod
    def level(score: int) -> str:
        if score == 0:
            return "SAFE"
        if score <= 25:
            return "GOOD"
        if score <= 60:
            return "MEDIUM"
        return "HIGH"
