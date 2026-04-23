# Installing Second Thought for Codex

## Quick install

1. Clone repository:

```bash
git clone https://github.com/gg-mo/second-thought-agent-skill.git ~/.codex/second-thought
```

2. Expose skills through Codex native discovery:

```bash
mkdir -p ~/.agents/skills
ln -sfn ~/.codex/second-thought/skills ~/.agents/skills/second-thought
```

3. Restart Codex.

## Verify

Confirm symlink exists:

```bash
ls -la ~/.agents/skills/second-thought
```
