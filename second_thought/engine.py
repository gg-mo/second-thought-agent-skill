"""Critique engines for the Second Thought skill."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .calibration import calibrate_confidence
from .models import (
    BlastRadius,
    CostLevel,
    CritiqueInput,
    CritiqueMode,
    CritiqueOutput,
    CritiqueStatus,
    ExplainabilityMode,
    Reversibility,
    RiskLevel,
    Stage,
)
from .scorers import AlignmentScorer, HeuristicAlignmentScorer, SemanticKeywordAlignmentScorer

AMBIGUITY_MARKERS: tuple[str, ...] = (
    "unclear",
    "not sure",
    "unknown",
    "tbd",
    "maybe",
    "depends",
    "unspecified",
)

ASSUMPTION_MARKERS: tuple[str, ...] = (
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
    mode: CritiqueMode = CritiqueMode.STRICT
    semantic_backend: str = "heuristic"  # heuristic | semantic_keyword
    confidence_slope: float = 1.0
    confidence_intercept: float = 0.0


class CritiqueEngine(ABC):
    @abstractmethod
    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        raise NotImplementedError


class RuleBasedCritiqueEngine(CritiqueEngine):
    def __init__(self, config: EngineConfig | None = None, scorer: AlignmentScorer | None = None) -> None:
        self.config = config or EngineConfig()
        self.scorer = scorer or _build_scorer(self.config.semantic_backend)

    def critique(self, payload: CritiqueInput) -> CritiqueOutput:
        if _is_low_signal_payload(payload):
            return CritiqueOutput(
                status=CritiqueStatus.PROMPT_HUMAN,
                summary="Not enough concrete proposal context to produce a reliable critique.",
                goal_alignment="Unknown due to insufficient proposal detail.",
                concerns=["The current request does not include a specific direction, plan, or action to evaluate."],
                assumptions=["Assuming the latest command was a critique invocation rather than the actual proposal."],
                better_options=["Provide the exact proposal you want critiqued or confirm I should critique the latest decision in context."],
                challenge_prompt="What is the exact proposal you want me to challenge before proceeding?",
                recommended_next_step="Ask one targeted clarification, then rerun critique against the concrete proposal.",
                prompt_to_human="What specific proposal or action should I critique right now?",
                confidence=0.32,
                decision_factors=["low_signal_input"],
            )

        mode = payload.mode if payload.mode is not None else self.config.mode
        alignment = self.scorer.score(payload)

        concerns: list[str] = []
        assumptions: list[str] = []
        better_options: list[str] = []
        decision_factors: list[str] = []

        if alignment < _alignment_floor(mode):
            concerns.append("The proposal appears weakly aligned with the original intent and may have drifted.")
            better_options.append(
                "Restate the goal in one sentence, then rewrite the proposal so each step clearly serves that goal."
            )
            decision_factors.append("low_alignment")
        elif alignment < _alignment_partial(mode):
            concerns.append("Alignment with the original intent is only partial; key parts of the ask may be under-covered.")
            better_options.append("Add explicit mapping from proposal steps to the original intent before locking this in.")
            decision_factors.append("partial_alignment")

        stage_strictness = _stage_strictness(payload.stage, mode)
        if payload.stage in (Stage.CONVERGENCE, Stage.PRE_EXECUTION):
            concerns.append("This is a high-commitment stage; verify that agreement came from correctness, not momentum.")
            decision_factors.append("high_commitment_stage")

        has_ambiguity = _contains_any(payload.current_context, AMBIGUITY_MARKERS) or _contains_any(
            payload.proposal, AMBIGUITY_MARKERS
        )
        if has_ambiguity:
            concerns.append("The direction is under-specified or ambiguous in ways that could cause incorrect execution.")
            decision_factors.append("ambiguity")

        if _contains_any(payload.rationale, ASSUMPTION_MARKERS):
            assumptions.append("The rationale includes uncertainty language that may hide unverified assumptions.")
            decision_factors.append("weak_rationale")

        assumptions.extend(_derive_constraint_assumptions(payload))

        if payload.risk_level == RiskLevel.HIGH:
            concerns.append("Risk is marked high, so unresolved uncertainty should be escalated before proceeding.")
            better_options.append("Add an explicit rollback or safety plan before taking irreversible or costly steps.")
            decision_factors.append("high_risk")

        if payload.reversibility == Reversibility.IRREVERSIBLE:
            concerns.append("The action is marked irreversible; require explicit confirmation before execution.")
            decision_factors.append("irreversible_action")

        if payload.estimated_cost == CostLevel.HIGH:
            concerns.append("Estimated cost is high; verify confidence and alternatives before committing resources.")
            decision_factors.append("high_cost")

        if payload.blast_radius in (BlastRadius.ORG, BlastRadius.PUBLIC):
            concerns.append("Blast radius is broad; this needs stronger safeguards and clearer ownership.")
            decision_factors.append("broad_blast_radius")

        if payload.should_challenge:
            concerns.append("The proposal should be stress-tested with a direct challenge question before acceptance.")
            decision_factors.append("challenge_requested")

        status = _decide_status(
            alignment=alignment,
            concern_count=len(concerns),
            has_ambiguity=has_ambiguity,
            risk_level=payload.risk_level,
            stage_strictness=stage_strictness,
            mode=mode,
            reversibility=payload.reversibility,
            estimated_cost=payload.estimated_cost,
            blast_radius=payload.blast_radius,
        )
        concerns = _ensure_context_specificity(concerns, payload)

        goal_alignment = _goal_alignment_text(alignment)
        summary = _summary_text(status, goal_alignment, payload.stage, concerns)
        challenge_prompt = _challenge_prompt()
        recommended_next_step = _recommended_next_step(status, payload.stage)
        prompt_to_human = _prompt_to_human(status, payload, decision_factors)

        if not concerns:
            concerns = ["No major blockers found, but monitor for drift as work progresses."]
        if not assumptions:
            assumptions = ["No explicit assumptions detected, but verify critical constraints before execution."]
        if not better_options:
            better_options = ["Proceed with lightweight checkpoints to confirm continued goal alignment."]
        if not decision_factors:
            decision_factors = ["aligned_and_low_risk"]

        decision_factors.append(f"alignment_score:{alignment:.3f}")

        raw_conf = _confidence_score_raw(status, alignment, len(concerns), has_ambiguity)
        confidence = calibrate_confidence(raw_conf, self.config.confidence_slope, self.config.confidence_intercept)

        output = CritiqueOutput(
            status=status,
            summary=summary,
            goal_alignment=goal_alignment,
            concerns=concerns,
            assumptions=assumptions,
            better_options=better_options,
            challenge_prompt=challenge_prompt,
            recommended_next_step=recommended_next_step,
            prompt_to_human=prompt_to_human,
            confidence=confidence,
            decision_factors=decision_factors,
        )
        return _apply_explainability(output, payload.explainability)


class FallbackCritiqueEngine(CritiqueEngine):
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
            and primary.confidence < 0.72
        )
        if not needs_escalation:
            return primary
        return self.fallback.critique(payload)


def _build_scorer(name: str) -> AlignmentScorer:
    if name == "semantic_keyword":
        return SemanticKeywordAlignmentScorer()
    return HeuristicAlignmentScorer()


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def _derive_constraint_assumptions(payload: CritiqueInput) -> list[str]:
    assumptions: list[str] = []
    proposal_bundle = f"{payload.proposal} {payload.current_context} {payload.rationale}".lower()
    for constraint in payload.constraints:
        words = [w for w in constraint.lower().split() if len(w) > 3]
        if words and not any(w in proposal_bundle for w in words):
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
    reversibility: Reversibility,
    estimated_cost: CostLevel,
    blast_radius: BlastRadius,
) -> CritiqueStatus:
    revise_threshold = 0.45 if mode == CritiqueMode.STRICT else 0.35
    concern_threshold = max(2, stage_strictness)
    if mode == CritiqueMode.FAST:
        concern_threshold = max(3, stage_strictness + 1)

    if reversibility == Reversibility.IRREVERSIBLE and risk_level != RiskLevel.LOW:
        return CritiqueStatus.PROMPT_HUMAN
    if estimated_cost == CostLevel.HIGH and blast_radius in (BlastRadius.ORG, BlastRadius.PUBLIC):
        return CritiqueStatus.PROMPT_HUMAN

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
    if mode == CritiqueMode.STRICT and concern_count >= max(2, concern_threshold - 1):
        return CritiqueStatus.REVISE
    return CritiqueStatus.PROCEED


def _goal_alignment_text(score: float) -> str:
    if score >= 0.7:
        return "Strong match to the original intent."
    if score >= 0.45:
        return "Partial match; some intent elements need tighter coverage."
    return "Weak match; current direction likely drifted from original intent."


def _summary_text(status: CritiqueStatus, goal_alignment: str, stage: Stage, concerns: list[str]) -> str:
    anchor = (concerns[0].rstrip(".") if concerns else "The proposal needs verification")
    if status == CritiqueStatus.PROCEED:
        return f"Proceed with a checkpoint. {goal_alignment} Key watchpoint: {anchor}."
    if status == CritiqueStatus.REVISE:
        return f"Revise before committing. {goal_alignment} In {stage.value}, address this first: {anchor}."
    return (
        f"Prompt the human/engineer before continuing. {goal_alignment} "
        f"Escalation reason: {anchor}."
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
        return f"Revise the proposal to close drift/assumption gaps, then rerun critique before leaving {stage.value}."
    return "Pause execution and ask the human/engineer a focused disambiguation question."


def _prompt_to_human(status: CritiqueStatus, payload: CritiqueInput, factors: list[str]) -> str | None:
    if status != CritiqueStatus.PROMPT_HUMAN:
        return None

    if "ambiguity" in factors:
        return (
            "Before I continue, which exact outcome do you want to optimize for first, and what trade-off is acceptable? "
            "Please choose one primary objective so I can avoid drifting."
        )

    if "irreversible_action" in factors:
        return "This step is irreversible. Do you want me to proceed now, or should I add a safety gate/approval checkpoint first?"

    if "high_cost" in factors or "broad_blast_radius" in factors:
        return "This has high cost or broad impact. What is your risk tolerance: conservative rollout, phased rollout, or full rollout?"

    return (
        "Before we continue, can you confirm whether this direction should optimize for "
        f"'{payload.original_intent}' even if it increases complexity, or do you want a "
        "simpler trade-off with reduced coverage?"
    )


def _confidence_score_raw(status: CritiqueStatus, alignment: float, concern_count: int, has_ambiguity: bool) -> float:
    base = alignment
    penalty = (concern_count * 0.06) + (0.12 if has_ambiguity else 0.0)
    raw = max(0.05, min(0.99, base - penalty + 0.25))
    if status == CritiqueStatus.PROMPT_HUMAN:
        raw = min(raw, 0.7)
    return raw


def _apply_explainability(output: CritiqueOutput, explainability: ExplainabilityMode) -> CritiqueOutput:
    if explainability == ExplainabilityMode.STANDARD:
        return output

    if explainability == ExplainabilityMode.COMPACT:
        output.concerns = output.concerns[:2]
        output.assumptions = output.assumptions[:1]
        output.better_options = output.better_options[:1]
        output.decision_factors = output.decision_factors[:3]
        output.summary = output.summary.split(". ")[0].strip()
        return output

    # detailed
    if len(output.concerns) < 3:
        output.concerns.append("Detailed mode enabled: review all listed factors before execution.")
    if len(output.better_options) < 2:
        output.better_options.append("Document why chosen path beats alternatives to reduce future drift.")
    return output


def _is_low_signal_payload(payload: CritiqueInput) -> bool:
    proposal = payload.proposal.strip().lower()
    context = payload.current_context.strip().lower()
    command_like = proposal in {
        "second-thought",
        "second thought",
        "use second-thought",
        "critique this",
        "run critique",
    }
    placeholder = proposal == "proceed with the currently implied direction."
    short = len(proposal.split()) <= 3
    missing_context = context.startswith("single-turn context:") or context.startswith("context unavailable")
    return (command_like or placeholder or short) and missing_context


def _ensure_context_specificity(concerns: list[str], payload: CritiqueInput) -> list[str]:
    specific = list(concerns)
    text = " ".join(c.lower() for c in specific)
    proposal_words = [w.lower() for w in payload.proposal.split() if len(w) > 4][:5]
    has_anchor = any(w in text for w in proposal_words)
    if not has_anchor and proposal_words:
        snippet = payload.proposal.strip()
        if len(snippet) > 120:
            snippet = f"{snippet[:117]}..."
        specific.insert(0, f"The current proposal ('{snippet}') needs stronger evidence of fit to the original intent.")
    return specific
