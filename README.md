# rpg-npc-cli

A local-first, beginner-friendly command-line tool that generates tabletop RPG
NPCs and campaign notes through a configurable OpenAI-compatible endpoint
(default Ollama). Saves locally as Markdown or JSON, ready to print. No API
keys required. MIT licensed.

## Who this is for

This is a fan project by **Asdale Dynamics, LLC** (Indiana, formed October
2026) — the small business founded by Dylan Asdale, a registered nurse turned
AI author. Dylan writes *The Massive AI Manual* and runs the hub site
dylanasdale.github.io, explaining AI "like a friend would": plain English,
step by step, never condescending.

Asdale Dynamics publishes beginner-friendly AI education, practical open-source
tools, and small-business / author resources. This CLI is one of those tools —
a small, useful, local-first utility for tabletop gamers, DMs, and anyone
learning to work with local LLMs.

## Features

* **NPC generation** — name, race, class, level, alignment, ability scores,
  hit points, armor class, skills, equipment, description, appearance,
  personality traits, ideals, bonds, flaws
* **Campaign notes** — title, content, date, tags, NPCs, locations, plot hooks
* **Configurable endpoint** — any OpenAI-compatible chat/completions API
  (default: Ollama at `http://localhost:11434/v1`)
* **Local-first** — works entirely offline. If no endpoint is reachable, the
  tool falls back to built-in local templates so you always get usable output.
* **Printable output** — clean Markdown (and JSON) files you can print or drop
  into any note-taking app
* **No secrets, no keys** — nothing is logged, stored, or sent anywhere except
  the endpoint you configure

## Install

```bash
# From this folder
pip install .
# or, with the console script available as `rpg`
rpg --help
```

No installation is required to run from source:

```bash
python -m rpg_cli.cli --help
```

## Usage

Generate an NPC (falls back to local templates if Ollama isn't running):

```bash
rpg npc --name "Gimble" --race Gnome --class Wizard --level 3 \
  --alignment "Chaotic Neutral"
```

Generate a campaign note:

```bash
rpg note --title "The Broken Bridge" --content "The party crossed the river." \
  --tag river --tag travel
```

Save to a file:

```bash
rpg npc --name "Aldric" --format md -o aldric.md
rpg note --title "Session One" --format json -o session.json
```

Force local-only output (no LLM call at all):

```bash
rpg npc --name "Aldric" --no-llm
```

Options:

* `--endpoint` — OpenAI-compatible base URL (default `http://localhost:11434/v1`)
* `--model` — model name (default `llama3`)
* `--api-key` — API key, only if your endpoint requires one
* `--format` — `md` (default) or `json`
* `--output` / `-o` — write to file instead of stdout
* `--no-llm` — use local templates, skip the endpoint

## Output format

Markdown output is printable and human-readable, with sections for abilities,
description, appearance, skills, equipment, traits, ideals, bonds, and flaws.
JSON output is a plain object you can import into other tools.

## Testing

```bash
pip install pytest requests
pytest
```

Tests run entirely against a mocked endpoint — no network, no keys.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC.

## Credit

Built and published by **Asdale Dynamics, LLC** — beginner-friendly AI
education, open-source tools, and practical guides for authors, small
businesses, and curious learners.
