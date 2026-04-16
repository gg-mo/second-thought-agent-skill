"""Typed models for the Are You Sure critique skill."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ProposalType(StrEnum):
    IDEA = "idea"
    DECISION = "decision"
    DESIGN = "design"
    PLAN = "plan"
    ACTION = "action"
    TOOL_CALL = "tool_call"
    RESPONSE = "response"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Stage(StrEnum):
    BRAINSTORMING = "brainstorming"
    CONVERGENCE = "convergence"
    PRE_EXECUTION = "pre_execution"
    POST_FEEDBACK = "post_feedback"


class CritiqueMode(StrEnum):
    STRICT = "strict"
    FAST = "fast"


class Reversibility(StrEnum):
    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


class CostLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class BlastRadius(StrEnum):
    LOCAL = "local"
    TEAM = "team"
    ORG = "org"
    PUBLIC = "public"
    UNKNOWN = "unknown"


class CritiqueStatus(StrEnum):
    PROCEED = "proceed"
    REVISE = "revise"
    PROMPT_HUMAN = "prompt_human"


def _clean_text(value: str, field_name: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text


@dataclass(slots=True)
class CritiqueInput:
    original_intent: str
    current_context: str
    proposal_type: ProposalType
    proposal: str
    rationale: str
    constraints: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    stage: Stage = Stage.CONVERGENCE
    should_challenge: bool = True
    mode: CritiqueMode = CritiqueMode.STRICT
    reversibility: Reversibility = Reversibility.UNKNOWN
    estimated_cost: CostLevel = CostLevel.UNKNOWN
    blast_radius: BlastRadius = BlastRadius.UNKNOWN

    def __post_init__(self) -> None:
        self.original_intent = _clean_text(self.original_intent, "original_intent")
        self.current_context = _clean_text(self.current_context, "current_context")
        self.proposal = _clean_text(self.proposal, "proposal")
        self.rationale = _clean_text(self.rationale, "rationale")

        cleaned_constraints: list[str] = []
        for constraint in self.constraints:
            c = constraint.strip()
            if c:
                cleaned_constraints.append(c)
        self.constraints = cleaned_constraints

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CritiqueInput":
        return cls(
            original_intent=payload["original_intent"],
            current_context=payload["current_context"],
            proposal_type=ProposalType(payload["proposal_type"]),
            proposal=payload["proposal"],
            rationale=payload["rationale"],
            constraints=list(payload.get("constraints", [])),
            risk_level=RiskLevel(payload.get("risk_level", RiskLevel.MEDIUM)),
            stage=Stage(payload.get("stage", Stage.CONVERGENCE)),
            should_challenge=bool(payload.get("should_challenge", True)),
            mode=CritiqueMode(payload.get("mode", CritiqueMode.STRICT)),
            reversibility=Reversibility(payload.get("reversibility", Reversibility.UNKNOWN)),
            estimated_cost=CostLevel(payload.get("estimated_cost", CostLevel.UNKNOWN)),
            blast_radius=BlastRadius(payload.get("blast_radius", BlastRadius.UNKNOWN)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_intent": self.original_intent,
            "current_context": self.current_context,
            "proposal_type": self.proposal_type.value,
            "proposal": self.proposal,
            "rationale": self.rationale,
            "constraints": self.constraints,
            "risk_level": self.risk_level.value,
            "stage": self.stage.value,
            "should_challenge": self.should_challenge,
            "mode": self.mode.value,
            "reversibility": self.reversibility.value,
            "estimated_cost": self.estimated_cost.value,
            "blast_radius": self.blast_radius.value,
        }


@dataclass(slots=True)
class CritiqueOutput:
    status: CritiqueStatus
    summary: str
    goal_alignment: str
    concerns: list[str]
    assumptions: list[str]
    better_options: list[str]
    challenge_prompt: str
    recommended_next_step: str
    prompt_to_human: str | None = None
    confidence: float = 0.5
    decision_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "summary": self.summary,
            "goal_alignment": self.goal_alignment,
            "concerns": self.concerns,
            "assumptions": self.assumptions,
            "better_options": self.better_options,
            "challenge_prompt": self.challenge_prompt,
            "recommended_next_step": self.recommended_next_step,
            "prompt_to_human": self.prompt_to_human,
            "confidence": round(self.confidence, 3),
            "decision_factors": self.decision_factors,
        }
