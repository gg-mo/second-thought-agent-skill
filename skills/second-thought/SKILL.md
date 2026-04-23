---
name: are-you-sure
description: Use when an idea, decision, design, plan, response, tool call, or action is about to be accepted or executed, especially during brainstorming, convergence, and pre-execution where shallow agreement or goal drift may occur.
---

# Are You Sure

A standalone decision checkpoint engine that asks whether the current direction is actually right before the agent commits.

## Core rule

Before moving forward with a meaningful proposal, run a critique against the original intent, not just the latest turn.

Default behavior: auto-build the payload from conversation context. Do not require manual field entry unless the user explicitly wants manual/debug mode.

## Input contract

Provide these fields to the critique engine:

- `original_intent`
- `current_context`
- `proposal_type` (`idea | decision | design | plan | action | tool_call | response`)
- `proposal`
- `rationale`
- `constraints`
- `risk_level` (`low | medium | high`)
- `stage` (`brainstorming | convergence | pre_execution | post_feedback`)
- `should_challenge`

## Output contract

Produce this structured result internally:

- `status` (`proceed | revise | prompt_human`)
- `summary`
- `goal_alignment`
- `concerns`
- `assumptions`
- `better_options`
- `challenge_prompt`
- `recommended_next_step`
- `prompt_to_human`

## User-facing response contract

Default output should be human-readable, not raw JSON.

- Use a conversational response in a few sentences (about 2-4).
- Avoid rigid section labels like `Decision:`, `Why:`, `Next:` unless explicitly requested.
- Include the decision (`proceed | revise | prompt_human`) naturally in prose.
- Include at least one specific reason grounded in the current proposal/context.
- Include one concrete next step.
- If `prompt_human`, ask exactly one focused clarification question.

Only show full JSON when the human explicitly requests JSON/debug/contract format.

## Stage behavior

- `brainstorming`: exploratory but critical; do not reward weak framing
- `convergence`: skeptical; test if agreement is correctness vs momentum
- `pre_execution`: strict; verify reversibility, risk, missing information
- `post_feedback`: re-evaluate without overfitting to latest feedback

## Decision standard

- `proceed`: strong intent alignment, acceptable assumptions, no required human clarification
- `revise`: direction is promising but flawed, drifting, or weakly justified
- `prompt_human`: ambiguity, under-specification, high impact, irreversibility, or clear preference/judgment call needed

## Invocation moments

Invoke this skill when:

- discussion starts hardening into a decision
- a plan/design feels settled after back-and-forth
- a meaningful action/tool call is next
- the agent feels suspiciously "too sure"

## Execution note

Use the local engine if available:

```bash
python3 scripts/are_you_sure_cli.py --input path/to/input.json
```

For auto-fill mode (no manual schema fields required):

```bash
echo "We are about to merge a risky migration plan." | python3 scripts/are_you_sure_cli.py
```

Or call the package directly:

```python
from are_you_sure import CritiqueInput, RuleBasedCritiqueEngine
```
