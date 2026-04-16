"""Auto-fill helpers for building critique payloads from partial context."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .models import BlastRadius, CostLevel, ProposalType, Reversibility, RiskLevel, Stage


@dataclass(slots=True)
class ConversationMessage:
    role: str
    content: str


_CONSTRAINT_PATTERNS = (
    r"\bmust\b[^.?!\n]*",
    r"\bshould\b[^.?!\n]*",
    r"\brequire(?:d|ment)?\b[^.?!\n]*",
    r"\bcannot\b[^.?!\n]*",
    r"\bneed to\b[^.?!\n]*",
    r"\bnon[- ]negotiable\b[^.?!\n]*",
)


def build_payload_from_partial(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a valid critique payload from partial/freeform input."""
    raw_request = str(payload.get("request") or payload.get("message") or payload.get("proposal") or "").strip()
    messages = _normalize_messages(payload.get("history"))
    user_messages = [m.content for m in messages if m.role == "user" and m.content.strip()]

    original_intent = str(payload.get("original_intent") or "").strip() or _infer_original_intent(user_messages, raw_request)
    current_context = str(payload.get("current_context") or "").strip() or _infer_current_context(messages, raw_request)
    proposal = str(payload.get("proposal") or "").strip() or _infer_proposal(messages, raw_request)
    rationale = str(payload.get("rationale") or "").strip() or _infer_rationale(raw_request, current_context)
    constraints = payload.get("constraints")
    if constraints is None:
        constraints = _infer_constraints(" ".join(user_messages + [raw_request, current_context]))
    constraints = [str(c).strip() for c in constraints if str(c).strip()]

    proposal_type = payload.get("proposal_type") or _infer_proposal_type(f"{raw_request} {proposal}")
    risk_level = payload.get("risk_level") or _infer_risk_level(f"{raw_request} {proposal} {current_context}")
    stage = payload.get("stage") or _infer_stage(f"{raw_request} {proposal} {current_context}")
    should_challenge = bool(payload.get("should_challenge", True))

    reversibility = payload.get("reversibility") or _infer_reversibility(f"{raw_request} {proposal}")
    estimated_cost = payload.get("estimated_cost") or _infer_cost(f"{raw_request} {proposal} {current_context}")
    blast_radius = payload.get("blast_radius") or _infer_blast_radius(f"{raw_request} {proposal} {current_context}")

    built = dict(payload)
    built.update(
        {
            "original_intent": original_intent,
            "current_context": current_context,
            "proposal_type": proposal_type,
            "proposal": proposal,
            "rationale": rationale,
            "constraints": constraints,
            "risk_level": risk_level,
            "stage": stage,
            "should_challenge": should_challenge,
            "reversibility": reversibility,
            "estimated_cost": estimated_cost,
            "blast_radius": blast_radius,
        }
    )
    return built


def _normalize_messages(raw_history: Any) -> list[ConversationMessage]:
    if not raw_history:
        return []
    out: list[ConversationMessage] = []
    if isinstance(raw_history, list):
        for item in raw_history:
            if isinstance(item, dict):
                role = str(item.get("role") or "user").strip().lower() or "user"
                content = str(item.get("content") or item.get("text") or "").strip()
                if content:
                    out.append(ConversationMessage(role=role, content=content))
            elif isinstance(item, str):
                text = item.strip()
                if text:
                    out.append(ConversationMessage(role="user", content=text))
    return out


def _infer_original_intent(user_messages: list[str], raw_request: str) -> str:
    if user_messages:
        return user_messages[0]
    if raw_request:
        return raw_request
    return "Determine whether the proposed direction truly serves the user's goal before committing."


def _infer_current_context(messages: list[ConversationMessage], raw_request: str) -> str:
    if messages:
        tail = messages[-4:]
        joined = " | ".join(f"{m.role}: {m.content}" for m in tail)
        return joined[:1200]
    if raw_request:
        return f"Single-turn context: {raw_request}"
    return "Context unavailable; critique using available proposal signal only."


def _infer_proposal(messages: list[ConversationMessage], raw_request: str) -> str:
    if raw_request:
        return raw_request
    for m in reversed(messages):
        if m.role == "user":
            return m.content
    return "Proceed with the currently implied direction."


def _infer_rationale(raw_request: str, current_context: str) -> str:
    candidate = f"{raw_request} {current_context}"
    m = re.search(r"\b(?:because|since|so that)\b(.+)", candidate, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()[:400]
    return "Rationale not explicitly provided; evaluate based on inferred intent and proposal."


def _infer_constraints(text: str) -> list[str]:
    constraints: list[str] = []
    for pattern in _CONSTRAINT_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            c = match.group(0).strip(" .,:;-")
            if c and c not in constraints:
                constraints.append(c)
    return constraints[:6]


def _infer_proposal_type(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("tool", "command", "shell", "call api", "invoke")):
        return ProposalType.TOOL_CALL.value
    if any(k in lowered for k in ("reply", "respond", "message", "statement")):
        return ProposalType.RESPONSE.value
    if any(k in lowered for k in ("design", "architecture", "ux")):
        return ProposalType.DESIGN.value
    if any(k in lowered for k in ("plan", "roadmap", "steps")):
        return ProposalType.PLAN.value
    if any(k in lowered for k in ("decide", "decision", "finalize", "choose")):
        return ProposalType.DECISION.value
    if any(k in lowered for k in ("run", "execute", "deploy", "merge", "commit", "delete", "publish")):
        return ProposalType.ACTION.value
    return ProposalType.IDEA.value


def _infer_risk_level(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("production", "irreversible", "delete", "drop", "legal", "public", "downtime", "high risk")):
        return RiskLevel.HIGH.value
    if any(k in lowered for k in ("merge", "commit", "refactor", "migration", "costly", "impact")):
        return RiskLevel.MEDIUM.value
    return RiskLevel.LOW.value


def _infer_stage(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("brainstorm", "explore ideas", "ideate")):
        return Stage.BRAINSTORMING.value
    if any(k in lowered for k in ("pre execution", "pre-execution", "before executing", "about to run", "ship now")):
        return Stage.PRE_EXECUTION.value
    if any(k in lowered for k in ("feedback", "after review", "post feedback", "post-feedback")):
        return Stage.POST_FEEDBACK.value
    if any(k in lowered for k in ("finalize", "converge", "settled", "chosen direction")):
        return Stage.CONVERGENCE.value
    return Stage.CONVERGENCE.value


def _infer_reversibility(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("irreversible", "cannot undo", "drop table", "delete permanently")):
        return Reversibility.IRREVERSIBLE.value
    if any(k in lowered for k in ("rollback", "partially reversible", "difficult to reverse")):
        return Reversibility.PARTIALLY_REVERSIBLE.value
    if any(k in lowered for k in ("safe to revert", "reversible")):
        return Reversibility.REVERSIBLE.value
    return Reversibility.UNKNOWN.value


def _infer_cost(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("expensive", "high cost", "weeks", "migration", "rewrite")):
        return CostLevel.HIGH.value
    if any(k in lowered for k in ("moderate cost", "sprint", "non-trivial")):
        return CostLevel.MEDIUM.value
    return CostLevel.UNKNOWN.value


def _infer_blast_radius(text: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in ("public", "external", "customers", "all users")):
        return BlastRadius.PUBLIC.value
    if any(k in lowered for k in ("organization", "org-wide", "company-wide")):
        return BlastRadius.ORG.value
    if any(k in lowered for k in ("team", "multiple services")):
        return BlastRadius.TEAM.value
    if any(k in lowered for k in ("local", "single file", "single module")):
        return BlastRadius.LOCAL.value
    return BlastRadius.UNKNOWN.value
