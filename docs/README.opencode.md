# Second Thought for OpenCode

Install via plugin reference in `.opencode/INSTALL.md`.

The plugin auto-registers `skills/` and injects the `using-second-thought` bootstrap guidance in session startup.

It also adds an automatic checkpoint gate for high-commitment requests (for example commit/merge/deploy/destructive edits).

Bypass is one-shot and explicit: `[st:skip <reason>]` or `#st-skip`.
