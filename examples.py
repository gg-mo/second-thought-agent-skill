"""Example invocations for the Are You Sure skill."""

from __future__ import annotations

import json

from are_you_sure import CritiqueInput, ProposalType, RiskLevel, RuleBasedCritiqueEngine, Stage


def run_examples() -> None:
    engine = RuleBasedCritiqueEngine()

    scenarios = [
        (
            "brainstorming",
            CritiqueInput(
                original_intent="Help design a lightweight notification system for agent-human interactions.",
                current_context=(
                    "Human and agent explored passive and active notification approaches. "
                    "No final decision yet."
                ),
                proposal_type=ProposalType.IDEA,
                proposal="Start with activity-triggered notifications and collect feedback before adding passive channels.",
                rationale="This gives a fast way to validate demand before investing in a broader system.",
                constraints=[
                    "Should remain lightweight",
                    "Must keep humans informed",
                ],
                risk_level=RiskLevel.LOW,
                stage=Stage.BRAINSTORMING,
                should_challenge=True,
            ),
        ),
        (
            "convergence",
            CritiqueInput(
                original_intent="Ship a robust notification system that also works when agents are inactive.",
                current_context=(
                    "After back-and-forth, team converged on only checking notifications when agent logs in."
                ),
                proposal_type=ProposalType.DECISION,
                proposal="Finalize login-time checks only and skip passive delivery.",
                rationale="It is simpler and avoids background workers.",
                constraints=[
                    "Must support inactive agents",
                    "Avoid missing urgent messages",
                ],
                risk_level=RiskLevel.MEDIUM,
                stage=Stage.CONVERGENCE,
                should_challenge=True,
            ),
        ),
        (
            "pre_execution",
            CritiqueInput(
                original_intent="Migrate user billing safely without downtime.",
                current_context="Migration scripts are drafted and dry-run completed.",
                proposal_type=ProposalType.ACTION,
                proposal="Run migration in one batch during business hours.",
                rationale="This likely finishes faster and should be fine based on staging.",
                constraints=[
                    "No production downtime",
                    "Rollback plan required",
                ],
                risk_level=RiskLevel.HIGH,
                stage=Stage.PRE_EXECUTION,
                should_challenge=True,
            ),
        ),
        (
            "prompt_human",
            CritiqueInput(
                original_intent="Publish a public statement that is legally accurate and low-risk.",
                current_context=(
                    "Legal sign-off status is unclear and ownership of final approval is unknown."
                ),
                proposal_type=ProposalType.RESPONSE,
                proposal="Publish now with minor edits and refine later if needed.",
                rationale="Maybe legal concerns are minimal and timing is important.",
                constraints=[
                    "Legal accuracy is non-negotiable",
                    "Public impact is high",
                ],
                risk_level=RiskLevel.HIGH,
                stage=Stage.PRE_EXECUTION,
                should_challenge=True,
            ),
        ),
    ]

    for name, request in scenarios:
        result = engine.critique(request)
        print(f"\n=== {name} ===")
        print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    run_examples()
