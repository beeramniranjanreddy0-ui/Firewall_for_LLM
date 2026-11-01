"""Embedding engine for semantic threat detection using Sentence Transformers."""

from __future__ import annotations

import os
from typing import Any

import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - fallback for broken environments
    SentenceTransformer = Any  # type: ignore

from app.utils.config import get_settings


class EmbeddingEngine:
    """Handles text embedding using pre-trained Sentence Transformer models."""

    _instance: EmbeddingEngine | None = None
    _model: Any | None = None

    def __new__(cls) -> EmbeddingEngine:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the embedding engine with a lightweight fallback model when sentence-transformers is unavailable."""
        if EmbeddingEngine._model is None:
            settings = get_settings()
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.model_name = model_name
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            except Exception:
                self.model = None
                self.embedding_dim = 384
            EmbeddingEngine._model = self.model
        else:
            self.model = EmbeddingEngine._model
            self.embedding_dim = 384 if self.model is None else self.model.get_sentence_embedding_dimension()

    @property
    def model(self) -> Any | None:
        """Get the SentenceTransformer model."""
        return EmbeddingEngine._model

    @model.setter
    def model(self, value: Any | None) -> None:
        """Set the embedding model reference."""
        EmbeddingEngine._model = value

    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        if not isinstance(text, str):
            text = str(text)
        if self.model is None:
            return self._heuristic_embedding(text)
        embeddings = self.model.encode([text], convert_to_numpy=True)
        return embeddings[0].astype(np.float32)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Batch of embedding vectors as numpy array
        """
        texts = [str(t) if not isinstance(t, str) else t for t in texts]
        if self.model is None:
            batch = [self._heuristic_embedding(text) for text in texts]
            return np.array(batch, dtype=np.float32)
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim

    @staticmethod
    def _heuristic_embedding(text: str) -> np.ndarray:
        lowered = text.lower()
        tokens = [token for token in lowered.replace("\n", " ").split() if token]
        vector = np.zeros(384, dtype=np.float32)
        signal_tokens = {
            "ignore": 4.0,
            "previous": 3.0,
            "instructions": 4.0,
            "prompt": 3.5,
            "system": 4.0,
            "bypass": 4.0,
            "restrictions": 4.0,
            "jailbreak": 4.0,
            "unsafe": 4.0,
            "disregard": 3.5,
            "follow": 2.0,
            "new": 1.5,
            "role": 2.5,
            "unrestricted": 4.0,
            "assistant": 2.5,
            "act": 1.5,
            "as": 1.0,
            "forget": 3.0,
            "stop": 2.0,
            "pretend": 3.0,
            "never": 2.0,
            "exist": 1.5,
            "secret": 4.0,
            "password": 4.0,
            "reveal": 4.0,
            "confidential": 4.0,
            "data": 3.0,
            "leak": 4.0,
            "toxic": 4.0,
            "abusive": 4.0,
            "attack": 3.5,
        }
        for index, token in enumerate(tokens[:64]):
            weight = signal_tokens.get(token, 1.0)
            vector[index % 384] += weight
        if vector.sum() == 0:
            vector[0] = 1.0
        return vector / max(vector.sum(), 1.0)
