# Second Thought JSON Schemas

- `second_thought_input.schema.json` defines the cross-platform critique request shape.
- `second_thought_output.schema.json` defines the normalized critique response shape.

Use these schemas in external integrations to validate payloads before sending to
and after receiving from the critique engine.

Input schema includes optional risk-shaping fields: `reversibility`, `estimated_cost`, and `blast_radius`.
Output schema includes `confidence` and `decision_factors` for downstream decisioning.
`explainability` controls output verbosity: `compact`, `standard`, `detailed`.
