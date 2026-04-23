---
name: using-second-thought
description: Use when starting any conversation and before major decisions to ensure second-thought critique is auto-applied before commitment, especially in brainstorming, convergence, and pre-execution phases.
---

# Using Second Thought

## Rule

Before a major direction is accepted, run `second-thought` critique automatically.

Major direction includes:

- finalizing a design/plan
- taking a meaningful tool call or action
- committing to an execution path that is costly or hard to reverse

## Hybrid Trigger Model

Use a hybrid model:

1. Automatic gate at high-commitment moments.
2. Manual invocation available at any time.

Automatic gate should trigger when requests involve:

- committing/merging/shipping/deploying/publishing
- meaningful file edits, deletions, migrations, or refactors
- potentially destructive or irreversible actions
- high-cost, high-blast-radius, or under-specified execution steps

If a platform supports runtime message transforms or pre-action hooks, use those to trigger the gate automatically.
If not, enforce this via startup instructions and agent process discipline.

## Escape Hatch

Allow one-shot bypass when speed is intentionally prioritized:

- User can include `[st:skip <reason>]` or `#st-skip`.
- Agent should acknowledge the bypass reason explicitly.
- Bypass should not become default behavior.

## Priority

1. User instructions
2. Second Thought skills
3. Default behavior

## How to use

1. Capture/infer `original_intent`.
2. Summarize/infer `current_context`.
3. Build critique payload automatically.
4. Run the critique engine.
5. Follow `status` strictly:
- `proceed` -> continue with checkpoint discipline
- `revise` -> improve proposal and rerun critique
- `prompt_human` -> ask `prompt_to_human` before continuing
6. Present results in conversational human language by default (few sentences); keep raw JSON internal unless explicitly requested.

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
