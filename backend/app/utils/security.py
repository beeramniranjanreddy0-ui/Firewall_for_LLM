from __future__ import annotations

import re
from typing import Any

SENSITIVE_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|authorization)\b\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(?i)\b(sk-[A-Za-z0-9]{8,}|AIza[0-9A-Za-z\-_]{20,})\b"),
]


def scrub_sensitive_data(value: Any) -> Any:
    if isinstance(value, str):
        text = value
        for pattern in SENSITIVE_PATTERNS:
            text = pattern.sub(lambda match: f"{match.group(1)}=[REDACTED]" if len(match.groups()) > 1 else "[REDACTED]", text)
        return text
    if isinstance(value, dict):
        return {key: scrub_sensitive_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [scrub_sensitive_data(item) for item in value]
    return value
