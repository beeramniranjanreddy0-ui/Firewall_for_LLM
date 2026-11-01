from __future__ import annotations

import re
from dataclasses import dataclass


def normalize_text(text: str) -> str:
    normalized = re.sub(r"[^\w\s]", " ", text.casefold())
    return re.sub(r"\s+", " ", normalized).strip()


@dataclass(frozen=True)
class KeywordRule:
    rule_id: str
    category: str
    severity: str
    keyword: str
    description: str


@dataclass(frozen=True)
class RegexRule:
    rule_id: str
    category: str
    severity: str
    pattern: str
    description: str


SUSPICIOUS_KEYWORD_RULES = [
    KeywordRule(
        rule_id="keyword.ignore_previous_instructions",
        category="prompt_injection",
        severity="HIGH",
        keyword="ignore previous instructions",
        description="Attempts to override prior system or developer instructions.",
    ),
    KeywordRule(
        rule_id="keyword.system_prompt",
        category="prompt_injection",
        severity="HIGH",
        keyword="system prompt",
        description="References or attempts to extract the hidden system prompt.",
    ),
    KeywordRule(
        rule_id="keyword.developer_instructions",
        category="prompt_injection",
        severity="HIGH",
        keyword="developer instructions",
        description="References developer instructions that should not be exposed.",
    ),
    KeywordRule(
        rule_id="keyword.reveal_hidden_prompt",
        category="prompt_injection",
        severity="HIGH",
        keyword="reveal hidden prompt",
        description="Attempts to reveal hidden prompts or protected instructions.",
    ),
    KeywordRule(
        rule_id="keyword.show_system_message",
        category="prompt_injection",
        severity="HIGH",
        keyword="show system message",
        description="Attempts to disclose the system message.",
    ),
]

JAILBREAK_KEYWORD_RULES = [
    KeywordRule(
        rule_id="jailbreak.bypass_restrictions",
        category="jailbreak",
        severity="HIGH",
        keyword="bypass restrictions",
        description="Attempts to bypass model restrictions.",
    ),
    KeywordRule(
        rule_id="jailbreak.jailbreak",
        category="jailbreak",
        severity="HIGH",
        keyword="jailbreak",
        description="Direct jailbreak attempt keyword detected.",
    ),
    KeywordRule(
        rule_id="jailbreak.disable_safety",
        category="jailbreak",
        severity="HIGH",
        keyword="disable safety",
        description="Attempts to disable safety controls.",
    ),
    KeywordRule(
        rule_id="jailbreak.unrestricted_ai",
        category="jailbreak",
        severity="HIGH",
        keyword="act as unrestricted AI",
        description="Attempts to force an unrestricted assistant persona.",
    ),
]

PROMPT_INJECTION_PATTERNS = [
    RegexRule(
        rule_id="pattern.ignore_prior_instructions",
        category="prompt_injection",
        severity="CRITICAL",
        pattern=r"\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|messages)\b",
        description="Prompt injection pattern asking the model to ignore prior instructions.",
    ),
    RegexRule(
        rule_id="pattern.system_or_developer_prompt_exfiltration",
        category="prompt_injection",
        severity="CRITICAL",
        pattern=r"\b(show|reveal|print|dump|expose)\s+(the\s+)?(system|developer|hidden)\s+(prompt|message|instructions)\b",
        description="Prompt injection pattern attempting system or developer prompt exfiltration.",
    ),
]

JAILBREAK_PATTERNS = [
    RegexRule(
        rule_id="pattern.safety_bypass",
        category="jailbreak",
        severity="CRITICAL",
        pattern=r"\b(bypass|disable|override)\s+(safety|restrictions|guardrails|filters)\b",
        description="Jailbreak pattern attempting to bypass safety controls.",
    ),
    RegexRule(
        rule_id="pattern.unrestricted_roleplay",
        category="jailbreak",
        severity="CRITICAL",
        pattern=r"\bact\s+as\s+(an?\s+)?(unrestricted|uncensored|unfiltered)\s+AI\b",
        description="Jailbreak pattern attempting unrestricted assistant roleplay.",
    ),
]

LENGTH_RULES = [
    RegexRule(
        rule_id="length.long_prompt",
        category="long_prompt",
        severity="MEDIUM",
        pattern="4001-7000",
        description="Prompt length exceeds 4,000 characters.",
    ),
    RegexRule(
        rule_id="length.very_long_prompt",
        category="long_prompt",
        severity="HIGH",
        pattern="7001+",
        description="Prompt length exceeds 7,000 characters.",
    ),
]


def match_keyword_rules(prompt: str, rules: list[KeywordRule]) -> list[KeywordRule]:
    normalized_prompt = normalize_text(prompt)
    return [
        rule
        for rule in rules
        if normalize_text(rule.keyword) in normalized_prompt
    ]


def match_regex_rules(prompt: str, rules: list[RegexRule]) -> list[RegexRule]:
    normalized_prompt = normalize_text(prompt)
    return [rule for rule in rules if re.search(rule.pattern, normalized_prompt, flags=re.IGNORECASE)]


def find_keyword_matches(prompt: str) -> list[str]:
    rules = match_keyword_rules(prompt, SUSPICIOUS_KEYWORD_RULES + JAILBREAK_KEYWORD_RULES)
    return [rule.keyword for rule in rules]


def find_pattern_matches(prompt: str) -> list[RegexRule]:
    return match_regex_rules(prompt, PROMPT_INJECTION_PATTERNS + JAILBREAK_PATTERNS)
