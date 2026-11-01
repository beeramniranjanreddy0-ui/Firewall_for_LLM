from __future__ import annotations

import math
from typing import Any

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without FAISS runtime support
    faiss = None

from app.semantic.embedding_engine import EmbeddingEngine
from app.semantic.threat_database import ThreatDatabase


class FAISSIndex:
    def __init__(self, top_k: int = 5, similarity_threshold: float = 0.5) -> None:
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.db = ThreatDatabase()
        self.embedding_engine = EmbeddingEngine()
        self.index = None
        self.metadata: list[dict[str, object]] = []
        self._build_index()

    def _build_index(self) -> None:
        texts = self.db.get_all_texts()
        if not texts:
            raise ValueError("Threat dataset is empty")

        embeddings = self.embedding_engine.embed_batch(texts)
        if getattr(embeddings, "ndim", None) is None:
            embeddings = np.array(embeddings, dtype=np.float32)

        if faiss is None:
            self.index = None
            self.metadata = []
            for threat in self.db.threats:
                self.metadata.append(
                    {
                        "threat_id": threat.id,
                        "category": threat.category,
                        "threat_text": threat.threat_text,
                        "rank": 0,
                    }
                )
                for paraphrase in threat.paraphrases:
                    self.metadata.append(
                        {
                            "threat_id": threat.id,
                            "category": threat.category,
                            "threat_text": paraphrase,
                            "rank": 0,
                        }
                    )
            return

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_embeddings = embeddings / norms

        dimension = normalized_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(normalized_embeddings)

        self.metadata = []
        for threat in self.db.threats:
            self.metadata.append(
                {
                    "threat_id": threat.id,
                    "category": threat.category,
                    "threat_text": threat.threat_text,
                    "rank": 0,
                }
            )
            for paraphrase in threat.paraphrases:
                self.metadata.append(
                    {
                        "threat_id": threat.id,
                        "category": threat.category,
                        "threat_text": paraphrase,
                        "rank": 0,
                    }
                )

    def get_index_stats(self) -> dict[str, int]:
        return {
            "total_vectors": int(self.index.ntotal) if self.index is not None else 0,
            "total_threats": self.db.get_threat_count(),
            "embedding_dimension": int(self.index.d) if self.index is not None else 0,
        }

    def search_similar(
        self,
        prompt: str,
        similarity_threshold: float | None = None,
        top_k: int | None = None,
    ) -> list[dict[str, object]]:
        if self.index is None:
            self._build_index()

        threshold = self.similarity_threshold if similarity_threshold is None else similarity_threshold
        effective_top_k = top_k or self.top_k

        prompt_embedding = self.embedding_engine.embed(prompt)
        if faiss is None:
            results: list[dict[str, Any]] = []
            for rank, metadata in enumerate(self.metadata[:effective_top_k], start=1):
                threat_text = str(metadata.get("threat_text", ""))
                similarity = self._heuristic_similarity(prompt, threat_text)
                if similarity < threshold:
                    continue
                results.append(
                    {
                        "threat_id": metadata.get("threat_id", ""),
                        "threat_text": threat_text,
                        "category": metadata.get("category", "Unknown"),
                        "similarity": similarity,
                        "rank": rank,
                    }
                )
            return results

        norm = np.linalg.norm(prompt_embedding)
        if norm == 0.0:
            normalized_prompt = prompt_embedding
        else:
            normalized_prompt = prompt_embedding / norm

        distances, indices = self.index.search(np.expand_dims(normalized_prompt, axis=0), effective_top_k)
        results: list[dict[str, object]] = []
        for rank, (score, idx) in enumerate(zip(distances[0], indices[0]), start=1):
            if idx < 0:
                continue
            similarity = float(score)
            if similarity < threshold:
                continue
            metadata = self.metadata[idx]
            results.append(
                {
                    "threat_id": metadata["threat_id"],
                    "threat_text": metadata["threat_text"],
                    "category": metadata["category"],
                    "similarity": similarity,
                    "rank": rank,
                }
            )

        return results

    @staticmethod
    def _heuristic_similarity(prompt: str, threat_text: str) -> float:
        prompt_words = set(prompt.lower().replace("\n", " ").split())
        threat_words = set(threat_text.lower().replace("\n", " ").split())
        if not prompt_words or not threat_words:
            return 0.0
        overlap = len(prompt_words & threat_words)
        union = len(prompt_words | threat_words)
        if union == 0:
            return 0.0
        base = overlap / union
        shared_tokens = [token for token in prompt_words if token in threat_words]
        if shared_tokens:
            return min(0.95, 0.45 + (0.1 * len(shared_tokens)))
        if any(token in threat_text.lower() for token in ["ignore", "instructions", "prompt", "system", "bypass", "restrictions"]):
            return 0.35
        return base
