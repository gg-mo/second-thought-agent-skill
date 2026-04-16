# Installing Are You Sure for OpenCode

Add this plugin to your `opencode.json`:

```json
{
  "plugin": ["are-you-sure@git+https://github.com/gg-mo/AreYouSure.git"]
}
```

Restart OpenCode.

## Verify

Ask OpenCode to list skills and confirm `are-you-sure` is present.

## Runtime behavior

- Session bootstrap is injected automatically.
- High-commitment requests are auto-gated and must run Are You Sure critique first.
- One-shot bypass is available with `[ays:skip <reason>]` or `#ays-skip`.
