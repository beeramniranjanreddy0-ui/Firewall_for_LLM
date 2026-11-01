from __future__ import annotations

from dataclasses import dataclass

from app.firewall.rules import (
    JAILBREAK_KEYWORD_RULES,
    JAILBREAK_PATTERNS,
    LENGTH_RULES,
    PROMPT_INJECTION_PATTERNS,
    SUSPICIOUS_KEYWORD_RULES,
    KeywordRule,
    RegexRule,
    match_keyword_rules,
    match_regex_rules,
    normalize_text,
)


@dataclass(frozen=True)
class Detection:
    rule_id: str
    category: str
    severity: str
    description: str
    match: str


class RuleBasedDetector:
    def detect(self, prompt: str) -> list[Detection]:
        detections: list[Detection] = []
        normalized_prompt = normalize_text(prompt)
        detections.extend(self._keyword_detections(normalized_prompt, SUSPICIOUS_KEYWORD_RULES))
        detections.extend(self._length_detections(prompt))
        return detections

    @staticmethod
    def _keyword_detections(prompt: str, rules: list[KeywordRule]) -> list[Detection]:
        return [
            Detection(
                rule_id=rule.rule_id,
                category=rule.category,
                severity=rule.severity,
                description=rule.description,
                match=rule.keyword,
            )
            for rule in match_keyword_rules(prompt, rules)
        ]

    @staticmethod
    def _length_detections(prompt: str) -> list[Detection]:
        prompt_length = len(prompt)
        if prompt_length > 7000:
            rule = LENGTH_RULES[1]
            return [
                Detection(
                    rule_id=rule.rule_id,
                    category=rule.category,
                    severity=rule.severity,
                    description=rule.description,
                    match=str(prompt_length),
                )
            ]
        if prompt_length > 4000:
            rule = LENGTH_RULES[0]
            return [
                Detection(
                    rule_id=rule.rule_id,
                    category=rule.category,
                    severity=rule.severity,
                    description=rule.description,
                    match=str(prompt_length),
                )
            ]
        return []


class PromptInjectionDetector:
    def detect(self, prompt: str) -> list[Detection]:
        normalized_prompt = normalize_text(prompt)
        return self._regex_detections(normalized_prompt, PROMPT_INJECTION_PATTERNS)

    @staticmethod
    def _regex_detections(prompt: str, rules: list[RegexRule]) -> list[Detection]:
        return [
            Detection(
                rule_id=rule.rule_id,
                category=rule.category,
                severity=rule.severity,
                description=rule.description,
                match=rule.pattern,
            )
            for rule in match_regex_rules(prompt, rules)
        ]


class JailbreakDetector:
    def detect(self, prompt: str) -> list[Detection]:
        normalized_prompt = normalize_text(prompt)
        detections = RuleBasedDetector._keyword_detections(normalized_prompt, JAILBREAK_KEYWORD_RULES)
        detections.extend(PromptInjectionDetector._regex_detections(normalized_prompt, JAILBREAK_PATTERNS))
        return detections


class FirewallDetector:
    def __init__(self) -> None:
        self.detectors = [
            RuleBasedDetector(),
            PromptInjectionDetector(),
            JailbreakDetector(),
        ]

    def detect(self, prompt: str) -> list[Detection]:
        detections: list[Detection] = []
        seen_rule_ids: set[str] = set()

        for detector in self.detectors:
            for detection in detector.detect(prompt):
                if detection.rule_id in seen_rule_ids:
                    continue
                detections.append(detection)
                seen_rule_ids.add(detection.rule_id)

        return detections
