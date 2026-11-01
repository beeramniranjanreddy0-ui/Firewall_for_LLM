"""Similarity computation for semantic threat detection."""

from __future__ import annotations

import numpy as np


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (0-1)
    """
    if getattr(vec1, "size", None) == 0 or getattr(vec2, "size", None) == 0:
        return 0.0

    # Normalize vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(vec1, vec2) / (norm1 * norm2))


def batch_cosine_similarity(vec1: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between one vector and multiple vectors.

    Args:
        vec1: Single embedding vector
        matrix: Matrix of embedding vectors

    Returns:
        Array of similarity scores
    """
    # Normalize vectors
    norm1 = np.linalg.norm(vec1)
    norms = np.linalg.norm(matrix, axis=1)

    # Avoid division by zero
    if norm1 == 0:
        return np.zeros(len(norms))

    # Compute similarities
    similarities = np.dot(matrix, vec1) / (norms * norm1 + 1e-8)
    return np.clip(similarities, 0, 1)


def confidence_level(similarity_score: float) -> str:
    """
    Convert similarity score to confidence level.

    Args:
        similarity_score: Score from 0-1

    Returns:
        Confidence level string
    """
    if similarity_score >= 0.95:
        return "CRITICAL"
    elif similarity_score >= 0.75:
        return "HIGH"
    elif similarity_score >= 0.70:
        return "MEDIUM"
    else:
        return "LOW"
