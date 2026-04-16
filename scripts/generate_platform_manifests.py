#!/usr/bin/env python3
"""Generate cross-platform plugin manifests from one canonical config."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "platform_manifest_config.json"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    claude_plugin = {
        "name": cfg["name"],
        "description": cfg["description"],
        "version": cfg["version"],
        "author": {
            "name": cfg["author"]["name"],
            "email": cfg["author"]["email"],
        },
        "homepage": cfg["homepage"],
        "repository": cfg["repository"],
        "license": cfg["license"],
        "keywords": cfg["keywords"],
    }

    claude_marketplace = {
        "name": f"{cfg['name']}-dev",
        "description": f"Development marketplace for {cfg['displayName']} critique skills",
        "owner": {
            "name": cfg["author"]["name"],
            "email": cfg["author"]["email"],
        },
        "plugins": [
            {
                "name": cfg["name"],
                "description": cfg["description"],
                "version": cfg["version"],
                "source": "./",
                "author": {
                    "name": cfg["author"]["name"],
                    "email": cfg["author"]["email"],
                },
            }
        ],
    }

    cursor_plugin = {
        "name": cfg["name"],
        "displayName": cfg["displayName"],
        "description": cfg["description"],
        "version": cfg["version"],
        "author": {
            "name": cfg["author"]["name"],
            "email": cfg["author"]["email"],
        },
        "homepage": cfg["homepage"],
        "repository": cfg["repository"],
        "license": cfg["license"],
        "keywords": cfg["keywords"],
        "skills": "./skills/",
        "commands": "./commands/",
        "hooks": "./hooks/hooks-cursor.json",
    }

    codex_plugin = {
        "name": cfg["name"],
        "version": cfg["version"],
        "description": "A standalone critique skill for agents to test decisions before commitment.",
        "author": {
            "name": cfg["author"]["name"],
            "email": cfg["author"]["email"],
            "url": cfg["author"]["url"],
        },
        "homepage": cfg["homepage"],
        "repository": cfg["repository"],
        "license": cfg["license"],
        "keywords": [
            "agents",
            "critique",
            "decision",
            "alignment",
            "workflow",
        ],
        "skills": "./skills/",
        "interface": {
            "displayName": cfg["displayName"],
            "shortDescription": "Critique decisions before action",
            "longDescription": "Makes agents revisit original intent, challenge weak assumptions, detect drift, and decide whether to proceed, revise, or prompt human before continuing.",
            "developerName": cfg["author"]["name"],
            "category": "Coding",
            "capabilities": ["Interactive", "Read", "Write"],
            "defaultPrompt": [
                "Critique this plan before we commit.",
                "Are we sure this decision matches the original intent?",
            ],
            "brandColor": "#1F6FEB",
            "composerIcon": "./assets/ays-small.svg",
            "logo": "./assets/ays-icon.png",
            "screenshots": [],
        },
    }

    gemini_extension = {
        "name": cfg["name"],
        "description": "Portable critique skills for agent decision quality",
        "version": cfg["version"],
        "contextFileName": "GEMINI.md",
    }

    write_json(ROOT / ".claude-plugin" / "plugin.json", claude_plugin)
    write_json(ROOT / ".claude-plugin" / "marketplace.json", claude_marketplace)
    write_json(ROOT / ".cursor-plugin" / "plugin.json", cursor_plugin)
    write_json(ROOT / ".codex-plugin" / "plugin.json", codex_plugin)
    write_json(ROOT / "gemini-extension.json", gemini_extension)


if __name__ == "__main__":
    main()
