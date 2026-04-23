# Second Thought for Codex

Codex discovers skills from `~/.agents/skills/` at startup.

Use install instructions in [.codex/INSTALL.md](../.codex/INSTALL.md).

## How to use

- Ask Codex to use `second-thought`, or just proceed normally and let auto-triggering apply at high-commitment moments
- You do not need to manually fill schema fields; payload is inferred in the background by default
- Default output should be conversational (few sentences with decision + reason + next step); raw JSON is for explicit debug requests
- For intentional one-shot bypass, include `[st:skip <reason>]` or `#st-skip`
