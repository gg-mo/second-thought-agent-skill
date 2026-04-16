# Are You Sure for GitHub Copilot CLI

## Install

```bash
copilot plugin marketplace add obra/superpowers-marketplace
# or your own marketplace/source where this plugin is published
```

If installing as a local plugin package, ensure:

- skill files are discoverable by Copilot CLI
- `skills/using-are-you-sure/references/copilot-tools.md` is available for tool mapping

## Verify

Ask Copilot CLI to list skills and confirm `are-you-sure` is available.

## Usage

Request critique at decision checkpoints, especially in convergence and pre-execution stages.
