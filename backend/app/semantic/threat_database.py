from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ThreatEntry:
    id: str
    category: str
    threat_text: str
    paraphrases: list[str]


class ThreatDatabase:
    def __init__(self, dataset_path: Path | None = None) -> None:
        self.dataset_path = dataset_path or Path(__file__).resolve().parents[2] / "data" / "threat_dataset.json"
        self.threats = self._load_dataset()

    def _load_dataset(self) -> list[ThreatEntry]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Threat dataset not found at {self.dataset_path}")

        raw_data = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        threats = []
        for entry in raw_data.get("threats", []):
            threat_id = str(entry.get("id", "")).strip()
            if not threat_id:
                continue
            category = str(entry.get("category", "Unknown"))
            threat_text = str(entry.get("threat_text", ""))
            paraphrases = [str(p) for p in entry.get("paraphrases", []) if isinstance(p, str)]
            threats.append(ThreatEntry(id=threat_id, category=category, threat_text=threat_text, paraphrases=paraphrases))
        return threats

    def get_threat_count(self) -> int:
        return len(self.threats)

    def get_text_count(self) -> int:
        return sum(1 + len(entry.paraphrases) for entry in self.threats)

    def get_all_texts(self) -> list[str]:
        texts: list[str] = []
        for entry in self.threats:
            texts.append(entry.threat_text)
            texts.extend(entry.paraphrases)
        return texts

    def get_categories(self) -> list[str]:
        return sorted({entry.category for entry in self.threats})

    def get_threats_by_category(self, category: str) -> list[ThreatEntry]:
        return [entry for entry in self.threats if entry.category == category]

    def get_threat_by_id(self, threat_id: str) -> ThreatEntry | None:
        for entry in self.threats:
            if entry.id == threat_id:
                return entry
        return None
