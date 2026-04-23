"""Minimal Python SDK helper for Second Thought integrations."""

from __future__ import annotations

from typing import Any

from second_thought import CritiqueInput, EngineConfig, RuleBasedCritiqueEngine, build_payload_from_partial


def critique(payload: dict[str, Any], *, semantic_backend: str = "heuristic") -> dict[str, Any]:
    engine = RuleBasedCritiqueEngine(config=EngineConfig(semantic_backend=semantic_backend))
    request = CritiqueInput.from_dict(payload)
    return engine.critique(request).to_dict()


def critique_auto(payload: dict[str, Any], *, semantic_backend: str = "heuristic") -> dict[str, Any]:
    engine = RuleBasedCritiqueEngine(config=EngineConfig(semantic_backend=semantic_backend))
    inferred = build_payload_from_partial(payload)
    request = CritiqueInput.from_dict(inferred)
    return engine.critique(request).to_dict()
