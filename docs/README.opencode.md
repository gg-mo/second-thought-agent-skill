# Are You Sure for OpenCode

Install via plugin reference in `.opencode/INSTALL.md`.

The plugin auto-registers `skills/` and injects the `using-are-you-sure` bootstrap guidance in session startup.

It also adds an automatic checkpoint gate for high-commitment requests (for example commit/merge/deploy/destructive edits).

Bypass is one-shot and explicit: `[ays:skip <reason>]` or `#ays-skip`.
