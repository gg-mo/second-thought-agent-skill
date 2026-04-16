"""Rule-based critique engine for the Are You Sure skill.

The design is intentionally modular so this engine can be replaced by an
LLM-backed implementation later without changing input/output models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Final

from .models import CritiqueInput, CritiqueOutput, CritiqueStatus, RiskLevel, Stage


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


class CritiqueEngine(ABC):
    """Abstract critique engine contract for swap-in implementations."""

    @abstractmethod
    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        raise NotImplementedError


class RuleBasedCritiqueEngine(CritiqueEngine):
    """Portable deterministic critique engine.

    This implementation enforces intent checks, drift detection, stage-aware
    strictness, and explicit recommendation outcomes.
    """

    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        intent_score = _intent_alignment_score(payload.original_intent, payload.proposal)
        context_score = _intent_alignment_score(payload.original_intent, payload.current_context)
        combined_alignment = (intent_score * 0.7) + (context_score * 0.3)

        concerns: list[str] = []
        assumptions: list[str] = []
        better_options: list[str] = []

        if combined_alignment < 0.22:
            concerns.append(
                "The proposal appears weakly aligned with the original intent and may have drifted."
            )
            better_options.append(
                "Restate the goal in one sentence, then rewrite the proposal so each step clearly serves that goal."
            )
        elif combined_alignment < 0.4:
            concerns.append(
                "Alignment with the original intent is only partial; key parts of the ask may be under-covered."
            )
            better_options.append(
                "Add explicit mapping from proposal steps to the original intent before locking this in."
            )

        stage_strictness = _stage_strictness(payload.stage)

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
            alignment=combined_alignment,
            concern_count=len(concerns),
            has_ambiguity=any("ambiguous" in c or "under-specified" in c for c in concerns),
            risk_level=payload.risk_level,
            stage_strictness=stage_strictness,
        )

        goal_alignment = _goal_alignment_text(combined_alignment)
        summary = _summary_text(status, goal_alignment, payload.stage)
        challenge_prompt = _challenge_prompt(payload)
        recommended_next_step = _recommended_next_step(status, payload.stage)
        prompt_to_human = _prompt_to_human(status, payload)

        # Keep lists useful and non-empty for downstream consumers.
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


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def _intent_alignment_score(original_intent: str, candidate: str) -> float:
    intent_tokens = _tokenize(original_intent)
    candidate_tokens = _tokenize(candidate)
    if not intent_tokens:
        return 0.0
    overlap = intent_tokens.intersection(candidate_tokens)
    return len(overlap) / len(intent_tokens)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _derive_constraint_assumptions(payload: CritiqueInput) -> list[str]:
    assumptions: list[str] = []
    proposal_lower = payload.proposal.lower()
    for constraint in payload.constraints:
        key_terms = _tokenize(constraint)
        if key_terms and len(key_terms.intersection(_tokenize(proposal_lower))) == 0:
            assumptions.append(
                f"Constraint may be unmet or implicit: '{constraint}'."
            )
    return assumptions


def _stage_strictness(stage: Stage) -> int:
    if stage == Stage.BRAINSTORMING:
        return 1
    if stage == Stage.POST_FEEDBACK:
        return 2
    if stage == Stage.CONVERGENCE:
        return 3
    return 4  # pre_execution


def _decide_status(
    *,
    alignment: float,
    concern_count: int,
    has_ambiguity: bool,
    risk_level: RiskLevel,
    stage_strictness: int,
) -> CritiqueStatus:
    if has_ambiguity and (risk_level == RiskLevel.HIGH or stage_strictness >= 3):
        return CritiqueStatus.PROMPT_HUMAN
    if risk_level == RiskLevel.HIGH and (alignment < 0.4 or concern_count >= 3):
        return CritiqueStatus.PROMPT_HUMAN
    if alignment < 0.4 or concern_count >= max(2, stage_strictness):
        return CritiqueStatus.REVISE
    return CritiqueStatus.PROCEED


def _goal_alignment_text(score: float) -> str:
    if score >= 0.65:
        return "Strong match to the original intent."
    if score >= 0.4:
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


def _challenge_prompt(payload: CritiqueInput) -> str:
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
