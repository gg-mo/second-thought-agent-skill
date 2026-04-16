---
description: Invoke the are-you-sure skill to critique a direction before commitment
---

Use the `are-you-sure` skill and return structured critique output:

- status
- summary
- goal_alignment
- concerns
- assumptions
- better_options
- challenge_prompt
- recommended_next_step
- prompt_to_human

Automatic gate behavior:

- If the request implies high commitment (commit/merge/deploy/destructive edit/high-risk action), run this critique before execution.
- If user intentionally wants to bypass once, require `[ays:skip <reason>]` or `#ays-skip` and acknowledge the bypass reason before proceeding.
