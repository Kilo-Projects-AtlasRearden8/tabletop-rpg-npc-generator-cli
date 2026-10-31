"""Tests for storage: Markdown and JSON output."""

import json
from pathlib import Path

import pytest

from rpg_cli.models import NPC, CampaignNote
from rpg_cli.storage import save_markdown, save_json, npc_to_markdown, campaign_note_to_markdown


def test_npc_markdown_contains_key_fields(tmp_path):
    npc = NPC(
        name="Aldric", race="Human", class_name="Fighter", level=2,
        alignment="Lawful Good", abilities={"str": 16, "dex": 12, "con": 14,
                                            "int": 10, "wis": 11, "cha": 9},
        hit_points=20, armor_class=16, speed="30 ft.",
        skills=["Athletics"], equipment=["sword"],
        description="A brave fighter.",
        appearance="Tall and armored.",
        personality_traits=["honest"], ideals=["honor"],
        bonds=["the king"], flaws=["stubborn"],
    )
    text = npc_to_markdown(npc)
    assert "# Aldric" in text
    assert "Human" in text and "Fighter" in text and "Level" in text
    assert "**STR:** 16" in text
    assert "**Hit Points:** 20" in text
    assert "Athletics" in text
    assert "A brave fighter." in text
    assert "honest" in text


def test_campaign_note_markdown(tmp_path):
    note = CampaignNote(
        title="Session One", content="We fought goblins.", date="2026-10-31",
        tags=["combat"], npcs=["Goblin Chief"], locations=["Cave"],
        plot_hooks=["A map fragment."],
    )
    text = campaign_note_to_markdown(note)
    assert "# Session One" in text
    assert "We fought goblins." in text
    assert "Goblin Chief" in text
    assert "A map fragment." in text


def test_save_markdown_writes_file(tmp_path):
    npc = NPC(name="Ria", race="Elf", class_name="Ranger", level=1,
              alignment="Neutral Good")
    p = tmp_path / "ria.md"
    save_markdown(npc, p)
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "# Ria" in content


def test_save_json_writes_file(tmp_path):
    npc = NPC(name="Ria", race="Elf", class_name="Ranger", level=1,
              alignment="Neutral Good")
    p = tmp_path / "ria.json"
    save_json(npc, p)
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["name"] == "Ria"
    assert data["race"] == "Elf"

    note = CampaignNote(title="T", content="c")
    p2 = tmp_path / "note.json"
    save_json(note, p2)
    data2 = json.loads(p2.read_text(encoding="utf-8"))
    assert data2["title"] == "T"
