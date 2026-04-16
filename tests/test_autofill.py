from __future__ import annotations

import unittest

from are_you_sure import CritiqueInput, build_payload_from_partial


class AutoFillTests(unittest.TestCase):
    def test_builds_valid_payload_from_single_request(self) -> None:
        partial = {"request": "We are about to deploy this risky migration to production."}
        built = build_payload_from_partial(partial)
        payload = CritiqueInput.from_dict(built)
        self.assertTrue(payload.original_intent)
        self.assertTrue(payload.current_context)
        self.assertTrue(payload.proposal)
        self.assertTrue(payload.rationale)
        self.assertEqual(payload.risk_level.value, "high")

    def test_prefers_history_for_original_intent_and_context(self) -> None:
        partial = {
            "history": [
                {"role": "user", "content": "Design alerts that work when agents are inactive."},
                {"role": "assistant", "content": "We can do active-session checks first."},
                {"role": "user", "content": "Now we are ready to finalize this."},
            ],
            "request": "Finalize active-only notifications.",
        }
        built = build_payload_from_partial(partial)
        self.assertIn("inactive", built["original_intent"].lower())
        self.assertIn("assistant:", built["current_context"].lower())
        self.assertEqual(built["stage"], "convergence")


if __name__ == "__main__":
    unittest.main()
