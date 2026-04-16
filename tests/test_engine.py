from __future__ import annotations

import unittest

from are_you_sure import (
    BlastRadius,
    CritiqueInput,
    CritiqueMode,
    CritiqueStatus,
    EngineConfig,
    ExplainabilityMode,
    FallbackCritiqueEngine,
    ProposalType,
    Reversibility,
    RiskLevel,
    RuleBasedCritiqueEngine,
    Stage,
)


class DummyFallbackEngine:
    def critique(self, payload: CritiqueInput):
        out = RuleBasedCritiqueEngine().critique(payload)
        out.confidence = min(out.confidence, 0.69)
        return out


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
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 1)
        self.assertIsInstance(result.decision_factors, list)

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
            reversibility=Reversibility.IRREVERSIBLE,
            blast_radius=BlastRadius.PUBLIC,
        )

        result = self.engine.critique(request)

        self.assertEqual(result.status, CritiqueStatus.PROMPT_HUMAN)
        self.assertTrue((result.prompt_to_human or ""))

    def test_fast_mode_reduces_false_revise_for_low_risk_ideation(self) -> None:
        request = CritiqueInput(
            original_intent="Explore onboarding ideas and shortlist one for prototyping.",
            current_context="We are still ideating and no decision is locked.",
            proposal_type=ProposalType.IDEA,
            proposal="Prototype one concise checklist flow and gather quick user feedback.",
            rationale="This keeps scope small while still learning what works.",
            constraints=["Keep iteration lightweight"],
            risk_level=RiskLevel.LOW,
            stage=Stage.BRAINSTORMING,
            should_challenge=False,
            mode=CritiqueMode.FAST,
        )

        result = self.engine.critique(request)

        self.assertEqual(result.status, CritiqueStatus.PROCEED)

    def test_explainability_compact_reduces_payload_size(self) -> None:
        request = CritiqueInput(
            original_intent="Plan migration safely.",
            current_context="Several concerns exist and alignment is partial.",
            proposal_type=ProposalType.PLAN,
            proposal="Proceed with minimal checks.",
            rationale="Likely fine.",
            risk_level=RiskLevel.MEDIUM,
            stage=Stage.CONVERGENCE,
            explainability=ExplainabilityMode.COMPACT,
        )
        result = self.engine.critique(request)
        self.assertLessEqual(len(result.concerns), 2)
        self.assertLessEqual(len(result.decision_factors), 3)

    def test_semantic_keyword_backend_option(self) -> None:
        engine = RuleBasedCritiqueEngine(config=EngineConfig(semantic_backend="semantic_keyword"))
        request = CritiqueInput(
            original_intent="Design notifications for offline agents.",
            current_context="We need alerts even when bots are idle.",
            proposal_type=ProposalType.PLAN,
            proposal="Add a passive notification channel.",
            rationale="Covers inactive periods.",
        )
        result = engine.critique(request)
        self.assertIn(result.status, (CritiqueStatus.PROCEED, CritiqueStatus.REVISE))

    def test_fallback_engine_escalates_borderline_high_stakes_cases(self) -> None:
        primary = RuleBasedCritiqueEngine()
        fallback = DummyFallbackEngine()
        hybrid = FallbackCritiqueEngine(primary, fallback)

        request = CritiqueInput(
            original_intent="Migrate billing safely with no customer impact.",
            current_context="Converged on a plan but rollback assumptions remain.",
            proposal_type=ProposalType.PLAN,
            proposal="Proceed with migration after limited checks.",
            rationale="Likely fine and time efficient.",
            constraints=["No downtime"],
            risk_level=RiskLevel.HIGH,
            stage=Stage.CONVERGENCE,
            should_challenge=True,
        )

        result = hybrid.critique(request)

        self.assertIn(result.status, (CritiqueStatus.REVISE, CritiqueStatus.PROMPT_HUMAN))

    def test_low_signal_payload_prompts_human(self) -> None:
        request = CritiqueInput(
            original_intent="are-you-sure",
            current_context="Single-turn context: are-you-sure",
            proposal_type=ProposalType.IDEA,
            proposal="are-you-sure",
            rationale="Rationale not explicitly provided; evaluate based on inferred intent and proposal.",
            risk_level=RiskLevel.LOW,
            stage=Stage.CONVERGENCE,
        )
        result = self.engine.critique(request)
        self.assertEqual(result.status, CritiqueStatus.PROMPT_HUMAN)
        self.assertTrue(result.prompt_to_human)


if __name__ == "__main__":
    unittest.main()
