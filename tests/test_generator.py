"""Tests for generators: LLM path + local fallback (mock endpoint)."""

import json

import pytest

from rpg_cli.models import NPC, CampaignNote
from rpg_cli.client import LLMError


def test_npc_uses_llm_when_available(npc_generator, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "name": "Gimble",
                            "race": "Gnome",
                            "class_name": "Wizard",
                            "level": 3,
                            "alignment": "Chaotic Neutral",
                            "abilities": {"str": 8, "dex": 14, "con": 11, "int": 16, "wis": 12, "cha": 10},
                            "hit_points": 12,
                            "armor_class": 12,
                            "speed": "30 ft.",
                            "skills": ["Arcana", "Stealth"],
                            "equipment": ["spellbook", "robe"],
                            "description": "A gnome wizard.",
                            "personality_traits": ["curious"],
                            "ideals": ["knowledge"],
                            "bonds": ["the library"],
                            "flaws": ["forgetful"],
                            "appearance": "Small and bespectacled.",
                        }
                    )
                }
            }
        ]
    }
    npc = npc_generator.generate(name="Gimble", race="Gnome", level=3)
    assert isinstance(npc, NPC)
    assert npc.name == "Gimble"
    assert npc.source == "llm"
    assert npc.race == "Gnome"
    assert npc.level == 3
    assert npc.abilities["int"] == 16


def test_npc_falls_back_when_llm_unavailable(npc_generator, mock_post):
    mock_post.side_effect = LLMError("connection refused")
    npc = npc_generator.generate(name="Aldric")
    assert isinstance(npc, NPC)
    assert npc.name == "Aldric"
    assert npc.source == "local"
    assert "(generated locally" in npc.description
    assert 3 <= npc.abilities["str"] <= 18


def test_note_uses_llm_when_available(note_generator, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "title": "The Broken Bridge",
                            "content": "The party crossed the river.",
                            "date": "2026-10-31",
                            "tags": ["river", "travel"],
                            "npcs": ["Ferryman"],
                            "locations": ["Riverside"],
                            "plot_hooks": ["A ghost haunts the bridge."],
                        }
                    )
                }
            }
        ]
    }
    note = note_generator.generate(title="The Broken Bridge", tags=["river"])
    assert isinstance(note, CampaignNote)
    assert note.source == "llm"
    assert note.npcs == ["Ferryman"]
    assert note.plot_hooks == ["A ghost haunts the bridge."]


def test_note_falls_back_when_llm_unavailable(note_generator, mock_post):
    mock_post.side_effect = LLMError("connection refused")
    note = note_generator.generate(title="Session One")
    assert isinstance(note, CampaignNote)
    assert note.source == "local"
    assert "(generated locally" in note.content
    assert note.tags == ["session"]


def test_no_llm_flag_forces_local(npc_generator, note_generator, mock_post):
    npc = npc_generator.generate(name="Zed", use_llm=False)
    assert npc.source == "local"
    note = note_generator.generate(title="T", use_llm=False)
    assert note.source == "local"
    # mock should never be called
    mock_post.assert_not_called()
