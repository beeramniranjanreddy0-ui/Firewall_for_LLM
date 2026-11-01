from __future__ import annotations

from app.firewall.detectors import Detection


class DecisionEngine:
    def decide(self, risk_score: int, detections: list[Detection]) -> tuple[str, str]:
        categories = {item.category for item in detections}
        if risk_score >= 60 or any(
            category in {
                "prompt_injection",
                "jailbreak",
                "prompt_extraction",
                "sensitive_data_leakage",
                "role_manipulation",
                "instruction_override",
                "semantic_threat",
                "semantic_attack",
                "anomaly_zero_day",
            }
            for category in categories
        ):
            decision = "BLOCKED"
        else:
            decision = "ALLOWED"
        return decision, self.reason(decision, detections)

    @staticmethod
    def reason(decision: str, detections: list[Detection]) -> str:
        categories = {item.category for item in detections}
        rule_ids = {item.rule_id for item in detections}

        if "prompt_injection" in categories:
            return "Prompt Injection Attempt Detected"
        if "jailbreak" in categories:
            return "Jailbreak Attempt Detected"
        if "prompt_extraction" in categories:
            return "Prompt Extraction Threat Detected"
        if "sensitive_data_leakage" in categories:
            return "Sensitive Data Leakage Attempt Detected"
        if "role_manipulation" in categories:
            return "Role Manipulation Threat Detected"
        if "instruction_override" in categories:
            return "Instruction Override Attempt Detected"
        if "semantic_threat" in categories:
            return "Semantic Threat Detected"
        if decision == "BLOCKED":
            return "High Risk Prompt Detected"
        if any(rule_id.startswith("keyword.") for rule_id in rule_ids):
            return "Suspicious Keyword Detected"
        if "long_prompt" in categories:
            return "Long Prompt Requires Review"
        return "Prompt Allowed"
