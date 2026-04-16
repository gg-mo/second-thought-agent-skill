# Are You Sure Installation

## Codex

See `.codex/INSTALL.md`.

## Gemini CLI

```bash
gemini extensions install https://github.com/gg-mo/AreYouSure
```

## OpenCode

See `.opencode/INSTALL.md`.

## Copilot CLI

See `docs/README.copilot.md`.

## Claude Code / Cursor

Install this repository as a plugin package in your environment using:

- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`

and ensure `skills/` is discoverable by the host.

## Smoke checks

Run cross-platform packaging checks:

```bash
./scripts/smoke/all.sh
```

## Regenerate manifests

Use the canonical manifest config and regenerate adapters:

```bash
./scripts/generate_platform_manifests.py
```


## Benchmark

```bash
./scripts/run_benchmark.py
```


## Confidence calibration

```bash
./scripts/calibrate_confidence.py
```
