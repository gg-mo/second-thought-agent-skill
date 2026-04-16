from __future__ import annotations

import unittest

from are_you_sure import CritiqueInput, CritiqueStatus, ProposalType, RiskLevel, RuleBasedCritiqueEngine, Stage


class RuleBasedCritiqueEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RuleBasedCritiqueEngine()

    def test_brainstorming_returns_actionable_output(self) -> None:
        request = CritiqueInput(
            original_intent="Brainstorm onboarding improvements for new users.",
            current_context="Exploring multiple onboarding options and trade-offs.",
            proposal_type=ProposalType.IDEA,
            proposal="Try an interactive checklist for first-session setup.",
            rationale="Could improve confidence during initial setup.",
            constraints=["Keep onboarding lightweight"],
            risk_level=RiskLevel.LOW,
            stage=Stage.BRAINSTORMING,
            should_challenge=True,
        )

        result = self.engine.critique(request)

        self.assertIn(result.status, (CritiqueStatus.PROCEED, CritiqueStatus.REVISE))
        self.assertTrue(result.challenge_prompt)
        self.assertTrue(result.recommended_next_step)

    def test_convergence_is_more_critical(self) -> None:
        request = CritiqueInput(
            original_intent="Design alerts that work even when agents are inactive.",
            current_context="Discussion converged quickly on active-session-only checks.",
            proposal_type=ProposalType.DECISION,
            proposal="Finalize active-session-only notifications.",
            rationale="It is simple and likely good enough.",
            constraints=["Must work when inactive"],
            risk_level=RiskLevel.MEDIUM,
            stage=Stage.CONVERGENCE,
            should_challenge=True,
        )

        result = self.engine.critique(request)

        self.assertEqual(result.status, CritiqueStatus.REVISE)
        self.assertGreaterEqual(len(result.concerns), 2)

    def test_pre_execution_high_risk_can_prompt_human(self) -> None:
        request = CritiqueInput(
            original_intent="Execute production migration with no downtime.",
            current_context="Rollback ownership is unclear.",
            proposal_type=ProposalType.ACTION,
            proposal="Run full migration now during peak traffic.",
            rationale="Maybe this is fine and faster.",
            constraints=["No downtime", "Rollback required"],
            risk_level=RiskLevel.HIGH,
            stage=Stage.PRE_EXECUTION,
            should_challenge=True,
        )

        result = self.engine.critique(request)

        self.assertEqual(result.status, CritiqueStatus.PROMPT_HUMAN)
        self.assertIsNotNone(result.prompt_to_human)

    def test_under_specified_high_impact_prompts_human(self) -> None:
        request = CritiqueInput(
            original_intent="Publish legally safe external communication.",
            current_context="Legal review status is unclear and approver is unknown.",
            proposal_type=ProposalType.RESPONSE,
            proposal="Publish immediately; refine later if needed.",
            rationale="Probably okay and timing matters.",
            constraints=["Legal accuracy is mandatory"],
            risk_level=RiskLevel.HIGH,
            stage=Stage.PRE_EXECUTION,
            should_challenge=True,
        )

        result = self.engine.critique(request)

        self.assertEqual(result.status, CritiqueStatus.PROMPT_HUMAN)


if __name__ == "__main__":
    unittest.main()
