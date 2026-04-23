"""Alignment scorer backends for critique engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Final

from .models import CritiqueInput


STOPWORDS: Final[set[str]] = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
    "we",
    "this",
    "they",
    "their",
    "our",
    "should",
    "will",
}

SYNONYM_MAP: Final[dict[str, set[str]]] = {
    "notify": {"alert", "notification", "ping"},
    "inactive": {"offline", "idle", "away"},
    "safe": {"secure", "reliable", "low-risk"},
    "goal": {"intent", "objective", "target"},
    "plan": {"strategy", "roadmap", "approach"},
    "review": {"critique", "evaluate", "assess"},
}


class AlignmentScorer(ABC):
    @abstractmethod
    def score(self, payload: CritiqueInput) -> float:
        raise NotImplementedError


class HeuristicAlignmentScorer(AlignmentScorer):
    """Default lexical/coverage scorer."""

    def score(self, payload: CritiqueInput) -> float:
        proposal = _intent_alignment_score(payload.original_intent, payload.proposal)
        context = _intent_alignment_score(payload.original_intent, payload.current_context)
        rationale = _intent_alignment_score(payload.original_intent, payload.rationale)
        phrase = _phrase_coverage_score(payload.original_intent, f"{payload.proposal} {payload.current_context}")
        return (proposal * 0.4) + (context * 0.2) + (rationale * 0.15) + (phrase * 0.25)


class SemanticKeywordAlignmentScorer(AlignmentScorer):
    """Optional semantic-ish backend using synonym expansion.

    Lightweight and dependency-free fallback that improves alignment when wording
    differs but concepts are related.
    """

    def score(self, payload: CritiqueInput) -> float:
        intent = _expand_tokens(_tokenize(payload.original_intent))
        candidate = _expand_tokens(
            _tokenize(" ".join([payload.proposal, payload.current_context, payload.rationale]))
        )
        if not intent:
            return 0.0
        overlap = len(intent.intersection(candidate))
        return overlap / len(intent)


def _normalize_token(token: str) -> str:
    t = token.lower()
    for suffix in ("ing", "ed", "es", "s"):
        if len(t) > 5 and t.endswith(suffix):
            return t[: -len(suffix)]
    return t


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return {_normalize_token(w) for w in words if w not in STOPWORDS and len(w) > 2}


def _expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in list(tokens):
        expanded.update(SYNONYM_MAP.get(token, set()))
    return expanded


def _intent_alignment_score(original_intent: str, candidate: str) -> float:
    intent_tokens = _tokenize(original_intent)
    candidate_tokens = _tokenize(candidate)
    if not intent_tokens:
        return 0.0
    overlap = intent_tokens.intersection(candidate_tokens)
    return len(overlap) / len(intent_tokens)


def _phrase_coverage_score(original_intent: str, candidate: str) -> float:
    chunks = [c.strip() for c in re.split(r"[,.;:]|\band\b|\bor\b", original_intent.lower()) if c.strip()]
    if not chunks:
        return 0.0
    cand_tokens = _tokenize(candidate)
    hits = 0
    for chunk in chunks:
        chunk_tokens = [t for t in _tokenize(chunk) if len(t) > 3]
        if not chunk_tokens:
            continue
        matched = sum(1 for t in chunk_tokens if t in cand_tokens)
        if matched / len(chunk_tokens) >= 0.5:
            hits += 1
    return hits / len(chunks)
