"""Critique engines for the Are You Sure skill.

This module keeps a deterministic rule-based engine as the default and exposes
an optional fallback wrapper so callers can escalate to an LLM engine when
desired without changing schemas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Final

from .models import (
    CritiqueInput,
    CritiqueMode,
    CritiqueOutput,
    CritiqueStatus,
    RiskLevel,
    Stage,
)


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

AMBIGUITY_MARKERS: Final[tuple[str, ...]] = (
    "unclear",
    "not sure",
    "unknown",
    "tbd",
    "maybe",
    "depends",
    "unspecified",
)

ASSUMPTION_MARKERS: Final[tuple[str, ...]] = (
    "assume",
    "assuming",
    "probably",
    "likely",
    "should be fine",
    "might",
    "could",
)


@dataclass(slots=True)
class EngineConfig:
    """Configuration knobs for rule strictness.

    strict mode is safer for convergence/pre-execution; fast mode reduces
    friction during ideation by requiring stronger evidence before revise.
    """

    mode: CritiqueMode = CritiqueMode.STRICT


class CritiqueEngine(ABC):
    """Abstract critique engine contract for swap-in implementations."""

    @abstractmethod
    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        raise NotImplementedError


class RuleBasedCritiqueEngine(CritiqueEngine):
    """Portable deterministic critique engine.

    Uses a blend of lexical and semantic-ish coverage heuristics to reduce false
    revise decisions from raw token overlap alone.
    """

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()

    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        mode = payload.mode if payload.mode is not None else self.config.mode
        alignment = _alignment_score(payload)

        concerns: list[str] = []
        assumptions: list[str] = []
        better_options: list[str] = []

        if alignment < _alignment_floor(mode):
            concerns.append(
                "The proposal appears weakly aligned with the original intent and may have drifted."
            )
            better_options.append(
                "Restate the goal in one sentence, then rewrite the proposal so each step clearly serves that goal."
            )
        elif alignment < _alignment_partial(mode):
            concerns.append(
                "Alignment with the original intent is only partial; key parts of the ask may be under-covered."
            )
            better_options.append(
                "Add explicit mapping from proposal steps to the original intent before locking this in."
            )

        stage_strictness = _stage_strictness(payload.stage, mode)

        if payload.stage in (Stage.CONVERGENCE, Stage.PRE_EXECUTION):
            concerns.append(
                "This is a high-commitment stage; verify that agreement came from correctness, not momentum."
            )

        if _contains_any(payload.current_context, AMBIGUITY_MARKERS) or _contains_any(
            payload.proposal, AMBIGUITY_MARKERS
        ):
            concerns.append(
                "The direction is under-specified or ambiguous in ways that could cause incorrect execution."
            )

        if _contains_any(payload.rationale, ASSUMPTION_MARKERS):
            assumptions.append(
                "The rationale includes uncertainty language that may hide unverified assumptions."
            )

        assumptions.extend(_derive_constraint_assumptions(payload))

        if payload.risk_level == RiskLevel.HIGH:
            concerns.append(
                "Risk is marked high, so unresolved uncertainty should be escalated before proceeding."
            )
            better_options.append(
                "Add an explicit rollback or safety plan before taking irreversible or costly steps."
            )

        if payload.should_challenge:
            concerns.append(
                "The proposal should be stress-tested with a direct challenge question before acceptance."
            )

        status = _decide_status(
            alignment=alignment,
            concern_count=len(concerns),
            has_ambiguity=any("ambiguous" in c or "under-specified" in c for c in concerns),
            risk_level=payload.risk_level,
            stage_strictness=stage_strictness,
            mode=mode,
        )

        goal_alignment = _goal_alignment_text(alignment)
        summary = _summary_text(status, goal_alignment, payload.stage)
        challenge_prompt = _challenge_prompt()
        recommended_next_step = _recommended_next_step(status, payload.stage)
        prompt_to_human = _prompt_to_human(status, payload)

        if not concerns:
            concerns = ["No major blockers found, but monitor for drift as work progresses."]
        if not assumptions:
            assumptions = ["No explicit assumptions detected, but verify critical constraints before execution."]
        if not better_options:
            better_options = ["Proceed with lightweight checkpoints to confirm continued goal alignment."]

        return CritiqueOutput(
            status=status,
            summary=summary,
            goal_alignment=goal_alignment,
            concerns=concerns,
            assumptions=assumptions,
            better_options=better_options,
            challenge_prompt=challenge_prompt,
            recommended_next_step=recommended_next_step,
            prompt_to_human=prompt_to_human,
        )


class FallbackCritiqueEngine(CritiqueEngine):
    """Optional fallback wrapper.

    Use this when you want a primary deterministic engine with optional
    escalation to an LLM-backed engine for borderline high-stakes cases.
    """

    def __init__(self, primary: CritiqueEngine, fallback: CritiqueEngine | None = None) -> None:
        self.primary = primary
        self.fallback = fallback

    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        primary = self.primary.critique(payload)
        if self.fallback is None:
            return primary

        needs_escalation = (
            primary.status == CritiqueStatus.REVISE
            and payload.stage in (Stage.CONVERGENCE, Stage.PRE_EXECUTION)
            and payload.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH)
        )
        if not needs_escalation:
            return primary
        return self.fallback.critique(payload)


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return {_normalize_token(w) for w in words if w not in STOPWORDS and len(w) > 2}


def _normalize_token(token: str) -> str:
    t = token.lower()
    for suffix in ("ing", "ed", "es", "s"):
        if len(t) > 5 and t.endswith(suffix):
            return t[: -len(suffix)]
    return t


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
    cand = candidate.lower()
    hits = 0
    for chunk in chunks:
        chunk_tokens = [t for t in _tokenize(chunk) if len(t) > 3]
        if not chunk_tokens:
            continue
        matched = sum(1 for t in chunk_tokens if t in _tokenize(cand))
        if matched / len(chunk_tokens) >= 0.5:
            hits += 1
    return hits / len(chunks)


def _alignment_score(payload: CritiqueInput) -> float:
    proposal = _intent_alignment_score(payload.original_intent, payload.proposal)
    context = _intent_alignment_score(payload.original_intent, payload.current_context)
    rationale = _intent_alignment_score(payload.original_intent, payload.rationale)
    phrase = _phrase_coverage_score(payload.original_intent, f"{payload.proposal} {payload.current_context}")
    # Weighted blend to reduce false negatives from exact token mismatch.
    return (proposal * 0.4) + (context * 0.2) + (rationale * 0.15) + (phrase * 0.25)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _derive_constraint_assumptions(payload: CritiqueInput) -> list[str]:
    assumptions: list[str] = []
    proposal_tokens = _tokenize(f"{payload.proposal} {payload.current_context} {payload.rationale}")
    for constraint in payload.constraints:
        key_terms = _tokenize(constraint)
        if key_terms and len(key_terms.intersection(proposal_tokens)) == 0:
            assumptions.append(f"Constraint may be unmet or implicit: '{constraint}'.")
    return assumptions


def _stage_strictness(stage: Stage, mode: CritiqueMode) -> int:
    base = {
        Stage.BRAINSTORMING: 1,
        Stage.POST_FEEDBACK: 2,
        Stage.CONVERGENCE: 3,
        Stage.PRE_EXECUTION: 4,
    }[stage]
    if mode == CritiqueMode.FAST:
        return max(1, base - 1)
    return base


def _alignment_floor(mode: CritiqueMode) -> float:
    return 0.2 if mode == CritiqueMode.STRICT else 0.15


def _alignment_partial(mode: CritiqueMode) -> float:
    return 0.45 if mode == CritiqueMode.STRICT else 0.35


def _decide_status(
    *,
    alignment: float,
    concern_count: int,
    has_ambiguity: bool,
    risk_level: RiskLevel,
    stage_strictness: int,
    mode: CritiqueMode,
) -> CritiqueStatus:
    revise_threshold = 0.45 if mode == CritiqueMode.STRICT else 0.35
    concern_threshold = max(2, stage_strictness)
    if mode == CritiqueMode.FAST:
        concern_threshold = max(3, stage_strictness + 1)

    # Fast mode is intended to keep ideation moving when risk is low and no
    # critical ambiguity is present.
    if (
        mode == CritiqueMode.FAST
        and risk_level == RiskLevel.LOW
        and stage_strictness <= 1
        and not has_ambiguity
        and concern_count <= 1
    ):
        return CritiqueStatus.PROCEED

    if has_ambiguity and (risk_level == RiskLevel.HIGH or stage_strictness >= 3):
        return CritiqueStatus.PROMPT_HUMAN
    if risk_level == RiskLevel.HIGH and (alignment < revise_threshold or concern_count >= 3):
        return CritiqueStatus.PROMPT_HUMAN
    if alignment < revise_threshold or concern_count >= concern_threshold:
        return CritiqueStatus.REVISE
    return CritiqueStatus.PROCEED


def _goal_alignment_text(score: float) -> str:
    if score >= 0.7:
        return "Strong match to the original intent."
    if score >= 0.45:
        return "Partial match; some intent elements need tighter coverage."
    return "Weak match; current direction likely drifted from original intent."


def _summary_text(status: CritiqueStatus, goal_alignment: str, stage: Stage) -> str:
    if status == CritiqueStatus.PROCEED:
        return f"Proceed with checkpoints. {goal_alignment}"
    if status == CritiqueStatus.REVISE:
        return (
            f"Revise before committing. {goal_alignment} "
            f"The current stage ({stage.value}) needs stronger justification."
        )
    return (
        f"Prompt the human/engineer before continuing. {goal_alignment} "
        "Critical ambiguity or impact requires explicit human judgment."
    )


def _challenge_prompt() -> str:
    return (
        "Are we choosing this direction because it is truly the best fit for the "
        "original intent, or because it is currently the easiest path to agree on?"
    )


def _recommended_next_step(status: CritiqueStatus, stage: Stage) -> str:
    if status == CritiqueStatus.PROCEED:
        return "Proceed, but keep one explicit intent-alignment checkpoint at the next milestone."
    if status == CritiqueStatus.REVISE:
        return (
            "Revise the proposal to close drift/assumption gaps, then rerun critique "
            f"before leaving {stage.value}."
        )
    return "Pause execution and ask the human/engineer a focused disambiguation question."


def _prompt_to_human(status: CritiqueStatus, payload: CritiqueInput) -> str | None:
    if status != CritiqueStatus.PROMPT_HUMAN:
        return None
    return (
        "Before we continue, can you confirm whether this direction should optimize for "
        f"'{payload.original_intent}' even if it increases complexity, or do you want a "
        "simpler trade-off with reduced coverage?"
    )
