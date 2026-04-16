from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SchemaShapeTests(unittest.TestCase):
    def test_input_schema_includes_required_core_fields(self) -> None:
        schema = json.loads((ROOT / "schemas" / "are_you_sure_input.schema.json").read_text())
        required = set(schema["required"])
        self.assertTrue({"original_intent", "proposal", "rationale"}.issubset(required))

        props = schema["properties"]
        self.assertEqual(props["proposal_type"]["enum"], [
            "idea",
            "decision",
            "design",
            "plan",
            "action",
            "tool_call",
            "response",
        ])
        self.assertIn("reversibility", props)
        self.assertIn("estimated_cost", props)
        self.assertIn("blast_radius", props)

    def test_output_schema_has_fixed_status_enum(self) -> None:
        schema = json.loads((ROOT / "schemas" / "are_you_sure_output.schema.json").read_text())
        status_enum = schema["properties"]["status"]["enum"]
        self.assertEqual(status_enum, ["proceed", "revise", "prompt_human"])
        self.assertIn("confidence", schema["properties"])
        self.assertIn("decision_factors", schema["properties"])


if __name__ == "__main__":
    unittest.main()
