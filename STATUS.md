# STATUS

## What was built

`rpg-npc-cli` is a local-first, beginner-friendly command-line tool that
generates tabletop RPG NPCs and campaign notes through a configurable
OpenAI-compatible endpoint (default Ollama). It saves locally as Markdown or
JSON, is printable, and requires no API keys. MIT licensed.

Package layout:

- `src/rpg_cli/`
  - `models.py` — `NPC` and `CampaignNote` dataclasses with `to_dict()`
  - `client.py` — `LLMClient` over an OpenAI-compatible `/chat/completions`
    endpoint (default `http://localhost:11434/v1`, model `llama3`, no key)
  - `prompts.py` — system/user prompt templates for NPC and campaign note
    generation
  - `generator.py` — `NPCGenerator` / `CampaignNoteGenerator` with LLM-first
    behavior and a deterministic local fallback when no endpoint is reachable
  - `storage.py` — Markdown and JSON serialization (printable, clean)
  - `cli.py` — argparse CLI with `npc` and `note` subcommands
- `tests/` — 19 tests covering the client, generators, storage, and CLI
- `pyproject.toml` — packaging metadata + pytest config
- `LICENSE` — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage, features, install, testing; credits Asdale Dynamics, LLC
- `.gitignore` — Python build/test artifacts

## How to run

```bash
# From source (no install needed)
PYTHONPATH=src python3 -m rpg_cli.cli npc --name "Gimble" --race Gnome --class Wizard --level 3 --no-llm
PYTHONPATH=src python3 -m rpg_cli.cli note --title "Session One" --content "..." --tag combat

# Or install and use the console script
pip install .
rpg npc --name "Aldric"
rpg note --title "The Broken Bridge" --format json -o session.json
```

Options: `--endpoint`, `--model`, `--api-key`, `--format {md,json}`, `-o/--output`,
`--no-llm`. See `README.md` and `rpg --help`.

## Verification results

- `pytest` — **19 passed** (client, generator, storage, CLI), all against a
  mocked endpoint; no network, no keys.
- CLI smoke tests — verified:
  - `npc` Markdown output to stdout (printable, full sections)
  - `npc` JSON output to stdout
  - `npc` Markdown and JSON saved to files (`-o`)
  - `note` Markdown and JSON saved to files
  - `--help` usage text
  - error handling for missing command and unknown flags (exit code 2)
- Local fallback — confirmed the tool produces usable NPCs and notes with no
  LLM endpoint reachable (Ollama not running), so it works fully offline.

## Known gaps

- The LLM client targets OpenAI-compatible `/chat/completions`. Ollama's
  default `/api/chat` is not OpenAI-compatible; point `--endpoint` at an
  OpenAI-compatible proxy or use a compatible server.
- The local fallback is template-based (deterministic, seeded), not LLM-driven.
- No streaming output; generation is synchronous.
- No persistent config file; settings come from CLI flags and environment
  variables only.
- The project is a fan project by Asdale Dynamics, LLC, not affiliated with
  any game system or LLM provider.