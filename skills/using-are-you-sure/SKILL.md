---
name: using-are-you-sure
description: Use at the start of a session and before major decisions to ensure are-you-sure critique is applied before commitment, especially in brainstorming, convergence, and pre-execution phases.
---

# Using Are You Sure

## Rule

Before a major direction is accepted, run `are-you-sure` critique.

Major direction includes:

- finalizing a design/plan
- taking a meaningful tool call or action
- committing to an execution path that is costly or hard to reverse

## Priority

1. User instructions
2. Are You Sure skills
3. Default behavior

## How to use

1. Capture `original_intent` clearly.
2. Summarize `current_context`.
3. Build critique payload.
4. Run the critique engine.
5. Follow `status` strictly:
- `proceed` -> continue with checkpoint discipline
- `revise` -> improve proposal and rerun critique
- `prompt_human` -> ask `prompt_to_human` before continuing

## Platform mapping

If skill/tool names differ by platform, use the mapped equivalents in `references/`:

- `codex-tools.md`
- `copilot-tools.md`
- `gemini-tools.md`

## Anti-patterns

- treating agreement as proof
- validating the latest suggestion without checking original intent
- pushing forward with high-impact ambiguity
- giving generic caution without actionable guidance
