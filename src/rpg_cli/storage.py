"""Local storage: save NPCs and campaign notes as Markdown or JSON."""

import json
from pathlib import Path
from typing import Union

from .models import NPC, CampaignNote

PathLike = Union[str, Path]


def _header(title: str) -> str:
    return f"# {title}\n"


def npc_to_markdown(npc: NPC) -> str:
    lines = [
        _header(npc.name),
        f"**Race:** {npc.race}  |  **Class:** {npc.class_name}  |  **Level:** {npc.level}",
        f"**Alignment:** {npc.alignment}  |  **Source:** {npc.source}  |  **Created:** {npc.created_at}",
        "",
        "## Abilities",
        "",
    ]
    for ability in ["str", "dex", "con", "int", "wis", "cha"]:
        score = npc.abilities.get(ability, 0)
        mod = (score - 10) // 2
        sign = "+" if mod >= 0 else ""
        lines.append(f"- **{ability.upper()}:** {score} ({sign}{mod})")
    lines += [
        "",
        f"**Hit Points:** {npc.hit_points}",
        f"**Armor Class:** {npc.armor_class}",
        f"**Speed:** {npc.speed}",
        "",
        "## Description",
        "",
        npc.description or "(none provided)",
        "",
        "## Appearance",
        "",
        npc.appearance or "(none provided)",
        "",
    ]
    if npc.skills:
        lines += ["## Skills", ""] + [f"- {s}" for s in npc.skills] + [""]
    if npc.equipment:
        lines += ["## Equipment", ""] + [f"- {e}" for e in npc.equipment] + [""]
    for section, key in [
        ("Personality Traits", "personality_traits"),
        ("Ideals", "ideals"),
        ("Bonds", "bonds"),
        ("Flaws", "flaws"),
    ]:
        items = getattr(npc, key)
        if items:
            lines += [f"## {section}", ""] + [f"- {i}" for i in items] + [""]
    return "\n".join(lines)


def campaign_note_to_markdown(note: CampaignNote) -> str:
    lines = [
        _header(note.title),
        f"**Date:** {note.date}  |  **Source:** {note.source}  |  **Created:** {note.created_at}",
        "",
        "## Content",
        "",
        note.content or "(none provided)",
        "",
    ]
    if note.tags:
        lines += ["## Tags", ""] + [f"- {t}" for t in note.tags] + [""]
    if note.npcs:
        lines += ["## NPCs", ""] + [f"- {n}" for n in note.npcs] + [""]
    if note.locations:
        lines += ["## Locations", ""] + [f"- {l}" for l in note.locations] + [""]
    if note.plot_hooks:
        lines += ["## Plot Hooks", ""] + [f"- {h}" for h in note.plot_hooks] + [""]
    return "\n".join(lines)


def save_markdown(obj: Union[NPC, CampaignNote], path: PathLike) -> Path:
    path = Path(path)
    if isinstance(obj, NPC):
        text = npc_to_markdown(obj)
    else:
        text = campaign_note_to_markdown(obj)
    path.write_text(text, encoding="utf-8")
    return path


def save_json(obj: Union[NPC, CampaignNote], path: PathLike) -> Path:
    path = Path(path)
    path.write_text(
        json.dumps(obj.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
