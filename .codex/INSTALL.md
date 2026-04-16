# Installing Are You Sure for Codex

## Quick install

1. Clone repository:

```bash
git clone https://github.com/gg-mo/AreYouSure.git ~/.codex/are-you-sure
```

2. Expose skills through Codex native discovery:

```bash
mkdir -p ~/.agents/skills
ln -sfn ~/.codex/are-you-sure/skills ~/.agents/skills/are-you-sure
```

3. Restart Codex.

## Verify

Confirm symlink exists:

```bash
ls -la ~/.agents/skills/are-you-sure
```
