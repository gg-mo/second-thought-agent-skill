---
description: Invoke the are-you-sure skill to critique a direction before commitment
---

Use the `are-you-sure` skill.

Do this automatically:

- If the user gives only natural language, infer payload fields in the background.
- User should not need to manually provide `original_intent`, `current_context`, `proposal_type`, etc.
- Ask follow-up only when ambiguity blocks safe execution.

Compute structured critique output internally with:

- status
- summary
- goal_alignment
- concerns
- assumptions
- better_options
- challenge_prompt
- recommended_next_step
- prompt_to_human

Default user-facing response format:

- Do NOT print raw JSON by default.
- Give a concise human response:
  - `Decision:` proceed/revise/prompt_human
  - `Why:` 1-2 concrete reasons tied to the current proposal
  - `Next:` exact next step
  - If `prompt_human`, ask the single clarification question

Only return raw JSON when the user explicitly asks for JSON/debug/contract output.

Automatic gate behavior:

- If the request implies high commitment (commit/merge/deploy/destructive edit/high-risk action), run this critique before execution.
- If user intentionally wants to bypass once, require `[ays:skip <reason>]` or `#ays-skip` and acknowledge the bypass reason before proceeding.
