# Installing Second Thought for OpenCode

Add this plugin to your `opencode.json`:

```json
{
  "plugin": ["second-thought@git+https://github.com/gg-mo/second-thought-agent-skill.git"]
}
```

Restart OpenCode.

## Verify

Ask OpenCode to list skills and confirm `second-thought` is present.

## Runtime behavior

- Session bootstrap is injected automatically.
- High-commitment requests are auto-gated and must run Second Thought critique first.
- One-shot bypass is available with `[st:skip <reason>]` or `#st-skip`.
