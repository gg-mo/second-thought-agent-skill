"""Minimal Python SDK helper for Are You Sure integrations."""

from __future__ import annotations

from typing import Any

from are_you_sure import CritiqueInput, EngineConfig, RuleBasedCritiqueEngine


def critique(payload: dict[str, Any], *, semantic_backend: str = "heuristic") -> dict[str, Any]:
    engine = RuleBasedCritiqueEngine(config=EngineConfig(semantic_backend=semantic_backend))
    request = CritiqueInput.from_dict(payload)
    return engine.critique(request).to_dict()
