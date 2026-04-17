# Are You Sure

A lot of LLMs and agents have the same default personality:

**“Hell yeah brother👏🙌, incredible idea🧠💪, absolutely cooked🔥, let’s ship it 🚀🚚.”**

Unfortunately, enthusiasm is not judgment.

Too many agents are eager to agree, amplify, and move forward, even when the idea is undercooked, the plan drifted from the original ask, or the human really needed pushback instead of applause.

**Are You Sure** is the anti-hype skill. 


Because not every idea deserves a standing ovation. Some ideas deserve a second look.

---

## What is this?

**Are You Sure** is a reusable decision checkpoint engine that can be added to many kinds of agents.

It is a standalone decision checkpoint engine for agents that challenges decisions before they turn into action. Instead of overhyping every plan, it revisits the original human intent, questions weak assumptions, checks whether the current direction is actually the right one, and recommends when the agent should revise, challenge, or prompt the human / engineer before moving forward.

Its job is simple:

> before an agent commits to a direction, plan, decision, or action, make it stop and ask: **are you sure this is actually the right move?**

This skill is designed to work across different agent types and workflows. It is not limited to coding agents or implementation tasks. It can be attached to agents that brainstorm, plan, write, research, design, analyze, or take tool-based actions.

The point is not to make agents slower for the sake of it.

The point is to make them **less blindly agreeable, more goal-aligned, and more intellectually honest**.

In supported agent environments, **Are You Sure** can auto-trigger when a conversation starts hardening into a high-commitment decision or action (for example merge/deploy/destructive steps). You can also type `are-you-sure` at any point to run a manual checkpoint.

---
## How to use

**Are You Sure** can auto-trigger when a conversation starts hardening into a high-commitment decision or action.

You can also type `are-you-sure` at any point to run a manual checkpoint.

---

## Installation

Installation differs by platform.

### Codex (CLI or App)

Paste this to your agent:

```text
Follow the installation instructions here: https://github.com/gg-mo/AreYouSure/blob/main/.codex/INSTALL.md
```

### Gemini CLI

```bash
gemini extensions install https://github.com/gg-mo/AreYouSure
```

### OpenCode

Follow [.opencode/INSTALL.md](.opencode/INSTALL.md).

### Claude Code

Option A: Claude Code Plugin (recommended)

From within Claude Code, add the marketplace and install the plugin:

```bash
/plugin marketplace add gg-mo/AreYouSure
/plugin install are-you-sure@are-you-sure
```

Option B: local development marketplace (if you're testing local changes)

```bash
git clone https://github.com/gg-mo/AreYouSure.git ~/.claude/are-you-sure
/plugin marketplace add ~/.claude/are-you-sure/.claude-plugin/marketplace.json
/plugin install are-you-sure@are-you-sure
```

Option C: `CLAUDE.md` (per-project)

New project:

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/gg-mo/AreYouSure/main/CLAUDE.md
```

Existing project (append):

```bash
echo "" >> CLAUDE.md
curl https://raw.githubusercontent.com/gg-mo/AreYouSure/main/CLAUDE.md >> CLAUDE.md
```

### Cursor

Option A: install from marketplace (if available in your Cursor environment)

1. Open Cursor Agent chat.
2. Run:

```text
/add-plugin are-you-sure
```

3. Confirm install in the plugin manager.

Option B: local plugin install (recommended for this repo right now)

1. Clone locally:

```bash
git clone https://github.com/gg-mo/AreYouSure.git ~/.cursor/are-you-sure
```

2. In Cursor Agent chat, run:

```text
/add-plugin
```

3. Choose local/plugin manifest install and select:

```text
~/.cursor/are-you-sure/.cursor-plugin/plugin.json
```

Reference manifest in this repo: [.cursor-plugin/plugin.json](.cursor-plugin/plugin.json)

### GitHub Copilot CLI

Follow [docs/README.copilot.md](docs/README.copilot.md).

---

## Why this exists

LLMs and agents are often very good at sounding helpful while being a little too eager to agree.

That shows up in all kinds of ways:

- cheering on weak ideas,
- locking into a plan too early,
- mistaking momentum for correctness,
- following the latest instruction without checking it against the original goal,
- and pushing forward when they should have challenged, clarified, or escalated.

One of the most common failure modes is not lack of intelligence. It is **over-obedience**.

An agent hears an idea and responds with:
- “Yes”
- “Great idea”
- “Let’s do it”
- “That makes sense”

But sometimes the correct response is:
- “Maybe”
- “Not yet”
- “This drifted from the original goal”
- “This sounds good in the moment, but are we solving the right problem?”
- “We should challenge this before locking it in”

**Are You Sure** exists to create that moment of resistance.

Not useless negativity.  
Not random contrarianism.  
Not fake caution theater.

Just real critique, at the right time.

---

## The core idea

Agents should not blindly act on their first thought.

They also should not blindly validate every idea that emerges from a back-and-forth with a human or engineer.

A conversation can feel productive and still drift.
A decision can feel settled and still be wrong.
A plan can sound polished and still fail the original objective.

**Are You Sure** is built to catch that.

It asks the agent to:

- revisit the original human intent,
- compare the current proposal against that intent,
- question whether the latest direction is actually the right one,
- surface hidden assumptions or risks,
- consider whether a better path exists,
- and decide whether it should proceed, revise, or prompt the human / engineer.

---

## What it does

At meaningful checkpoints, the agent sends its current proposal through **Are You Sure**.

That proposal might be:

- an idea,
- a chosen direction,
- a design decision,
- a plan,
- a tool call,
- a risky next step,
- or an action the agent is about to take.

The skill then critiques that proposal in context.

It asks questions like:

- Does this still match the human’s original intent?
- Did the conversation drift toward something easier, louder, or more convenient rather than more correct?
- Is this decision based on assumptions that have not been verified?
- Is the agent prematurely locking in a direction?
- Is there a simpler, safer, or sharper alternative?
- Is this action reversible?
- Is this the moment to prompt the human or engineer instead of continuing?
- Is the agent being thoughtful, or just being agreeable?

It then returns structured guidance that helps the agent:

- **proceed**
- **revise**
- or **prompt the human / engineer**

---

## Where this skill matters most

### 1. During brainstorming
During ideation, agents should be collaborative and helpful, but not mindlessly validating everything.

If a human suggests a direction, the agent should explore it. But once a direction starts hardening into a real decision, the agent should step back and challenge it.

Agreement is not proof. Momentum is not proof. Excitement is not proof.

### 2. During decision convergence
This is one of the biggest targets of the skill.

A human and an agent may go back and forth, refine ideas together, and gradually converge on a plan. At that moment, many agents simply accept the result and move on.

**Are You Sure** does the opposite.

When a design, decision, or plan appears to be settling, it re-evaluates that outcome against the original intent and asks:

- Is this really it?
- Are we solving the actual problem?
- Did we converge because the direction is right, or because it was easy to agree on?
- Did anyone challenge the weak parts?

### 3. Before execution
Before a meaningful action is taken, the agent should run the decision through critique.

This is especially useful before:
- tool calls,
- code changes,
- file edits,
- destructive actions,
- external writes,
- public output,
- high-cost moves,
- or steps that are hard to reverse.

---


### Why this is different

Are You Sure is not just a pre-execution reviewer.

It is a **decision checkpoint engine** that specifically targets convergence risk: moments where agreement forms quickly and can be mistaken for correctness.

## Philosophy

The best agents are not the ones that always move fast.

They are not the ones that always agree.

They are the ones that know when to stop, revisit the original intent, question the current direction, and ask whether the next move actually deserves to happen.

**Are You Sure** is built around that mindset.

It is not trying to make agents timid.  
It is trying to make them **responsible**.

It is not trying to make agents argumentative.  
It is trying to make them **honest**.

It is not trying to make agents block progress.  
It is trying to make sure the agent is not confidently accelerating in the wrong direction.

---

## Design principles

### Goal-first, not action-first
Every critique starts by grounding itself in the original human goal, not just the latest message in the conversation.

### Challenge convergence, not just execution
The skill should not wait until implementation time. It should also challenge decisions when they begin to harden during discussion.

### Push back when needed
A good agent should not be a hype machine. Sometimes the right move is to challenge the direction rather than cheer it on.

### Prompt humans intentionally
If the path is ambiguous, high-impact, irreversible, or under-specified, the agent should be willing to pause and ask the human or engineer.

### Stay portable
This is meant to be a standalone skill that can be used by many different agents, stacks, and workflows.

### Improve thinking without killing momentum
Critique should be sharp and useful, not bloated or performative.

---

## What a strong critique looks like

A strong critique does not just say “this might be bad.”

It does things like:

- reconnect the current direction to the original ask,
- point out where the conversation drifted,
- identify weak or untested assumptions,
- flag risk, cost, or irreversibility,
- suggest a better alternative,
- call out premature certainty,
- recommend a clarification question,
- or explain why human input is needed before continuing.

A weak critique is vague, generic, or purely oppositional.

A strong critique is specific enough to improve the next step.

---

## Decision outcomes

Every review from **Are You Sure** should generally end in one of three outcomes.

### Proceed
The current proposal appears aligned, reasonable, and safe enough to continue.

### Revise
The current proposal has flaws, drift, weak assumptions, or a better alternative exists. The agent should improve it before moving forward.

### Prompt Human / Engineer
The path is ambiguous, under-specified, high-impact, or likely to benefit from human judgment. The agent should pause and ask instead of pretending certainty.

---

## Example use cases

### Coding agents
Before changing code, the agent can verify that the proposed change actually solves the user’s real problem, not just the symptom discussed most recently. It can also decide whether a broader change should be confirmed with the engineer first.

### Planning agents
Before finalizing a workflow, roadmap, or strategy, the agent can test whether the proposed path still matches the original objective and whether it is prematurely committing to a convenient but weak plan.

### Writing agents
Before drafting, rewriting, or finalizing content, the agent can verify that tone, structure, and argument still reflect the original ask rather than drifting into something polished but misaligned.

### Research agents
Before summarizing findings or making a recommendation, the agent can challenge whether the available evidence is actually sufficient and whether uncertainty should be stated more honestly.

### Design agents
Before settling on a product or UX direction, the agent can ask whether the chosen approach addresses the true user need or simply became the most discussable idea during collaboration.

### General-purpose assistants
Any agent involved in brainstorming, synthesis, or multi-step work can use this skill to avoid becoming a passive “yes machine.”

---

## Brainstorming and decision convergence

This skill is especially important in human-agent collaboration.

A lot of systems assume the dangerous part happens at execution time. But many bad outcomes begin earlier, at the moment when discussion turns into commitment.

A human proposes something.  
The agent builds on it.  
The conversation gains momentum.  
Everyone starts feeling good.  
A direction gets chosen.

That can look like progress. Sometimes it is.

Sometimes it is just unchallenged agreement.

**Are You Sure** is designed to catch that exact moment.

When a design, decision, or plan starts to solidify, the skill should step back and ask:

- Does this still reflect the original intent?
- Did the discussion drift?
- Are we locking this in because it is right, or because it is the latest thing everyone accepted?
- Are we rewarding confidence over correctness?
- Should the agent challenge this before moving forward?

The role of the skill is not to be annoying.  
The role of the skill is to prevent shallow convergence from being mistaken for good judgment.

---

## Intended integration style

**Are You Sure** is meant to be portable.

An agent should be able to call it whenever it has:

- a candidate next step,
- a proposed decision,
- a plan,
- a direction emerging from brainstorming,
- a tool call,
- a risky action,
- or uncertainty about whether to continue.

That means the skill should stay:

- standalone,
- reusable,
- lightweight enough to wrap around many workflows,
- and independent of any one framework or stack.

This is not meant to be locked into a single implementation style. It should be usable by all kinds of agents.

---

## Ideal moments to invoke the skill

Use **Are You Sure** when:

- a discussion is starting to turn into a decision,
- an agent wants to finalize a design or direction,
- the plan sounds good but has not been checked against the original goal,
- the agent is about to take a meaningful action,
- the proposed step is costly or hard to reverse,
- the agent is operating on incomplete context,
- the user’s real intent may have been lost,
- or the agent feels suspiciously “too sure.”

If the agent is about to say “great idea, let’s do it,” that is often a very good time to run **Are You Sure**.

---

## Non-goals

This skill is **not** trying to:

- reject every idea,
- slow down every workflow unnecessarily,
- be contrarian for the sake of it,
- replace human judgment,
- or create fake rigor through generic caution.

It is also not only for implementation review.

Its job is broader than that:
- challenge emerging decisions,
- catch goal drift,
- and improve the quality of commitment before action happens.

---

## Summary

**Are You Sure** is a standalone decision checkpoint engine for agents.

It helps agents stop overhyping every idea, revisit the original human intent, challenge weak or drifting decisions, and determine whether they should proceed, revise, or prompt the human / engineer before moving forward.

In short:

**it helps agents think twice before they do something once.**

---

## Implementation in this repo

This repository now includes both:

- a reusable Python critique engine (`are_you_sure/`), and
- portable skill/plugin scaffolding for multiple coding agents (`skills/`, plugin manifests, and install docs).

### Core code

- `are_you_sure/models.py` - typed input/output schemas
- `are_you_sure/engine.py` - modular rule-based critique engine
- `are_you_sure/prompts.py` - LLM critique prompt and prompt builder
- `scripts/are_you_sure_cli.py` - CLI wrapper (`stdin` or `--input` JSON)

### Skills

- `skills/are-you-sure/SKILL.md` - core decision checkpoint contract
- `skills/using-are-you-sure/SKILL.md` - startup/process wrapper for consistent usage

### Platform integration files

- Claude plugin manifest: `.claude-plugin/plugin.json`
- Cursor plugin manifest: `.cursor-plugin/plugin.json`
- Codex plugin manifest: `.codex-plugin/plugin.json`
- Codex install guide: `.codex/INSTALL.md`
- Gemini extension manifest: `gemini-extension.json` + `GEMINI.md`
- OpenCode plugin: `.opencode/plugins/are-you-sure.js` + `.opencode/INSTALL.md`
- Session-start hooks: `hooks/`

### Hybrid trigger model (auto-gate + manual escape hatch)

Are You Sure now uses a hybrid trigger model:

- Automatic gates at high-commitment moments.
- Manual invocation remains available for explicit checkpointing.

Automatic gates are currently implemented in OpenCode plugin runtime transforms, and startup behavior is enforced across other integrations through `using-are-you-sure` bootstrap instructions.

High-commitment trigger examples:

- commit/merge/deploy/release/publish intent
- destructive or irreversible actions
- costly/high-impact execution steps
- major edits/refactors/migrations

One-shot bypass (manual escape hatch):

- `[ays:skip <reason>]`
- `#ays-skip`

Bypass should be acknowledged explicitly and used intentionally, not as default behavior.

---

## Run the critique engine

```bash
python3 scripts/are_you_sure_cli.py --input payload.json
```

Or:

```bash
cat payload.json | python3 scripts/are_you_sure_cli.py
```

Auto-fill mode (default, no manual schema fields required):

```bash
echo "We are about to deploy a risky migration; are we sure?" | python3 scripts/are_you_sure_cli.py
```

Strict manual mode:

```bash
python3 scripts/are_you_sure_cli.py --input payload.json --input-mode manual
```

For agent chat UX, keep JSON as an internal contract and return a short conversational critique by default (a few sentences). Only emit raw JSON when explicitly requested for debugging/integration.

Payload schema is the same cross-platform skill contract described in the `are-you-sure` skill and in the Python models.


Schemas: see `schemas/are_you_sure_input.schema.json` and `schemas/are_you_sure_output.schema.json` for integration validation.
### Manifest source of truth

Platform manifests are generated from `config/platform_manifest_config.json`.

Regenerate with:

```bash
./scripts/generate_platform_manifests.py
```


## Benchmarking

Run fixture benchmark scenarios:

```bash
./scripts/run_benchmark.py
```

The benchmark currently enforces a minimum pass rate of 75%.


## SDK helpers

- Python helper: `sdk/python/are_you_sure_sdk.py`
- TypeScript helper: `sdk/ts/index.ts`


## API contract

- Versioned contract: `docs/api/v1.md`
- Contract changelog: `docs/api/changelog.md`


## Confidence calibration

```bash
./scripts/calibrate_confidence.py
./scripts/run_benchmark.py
```
