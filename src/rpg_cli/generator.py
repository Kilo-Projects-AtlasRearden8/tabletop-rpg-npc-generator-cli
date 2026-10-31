"""NPC and campaign note generation with LLM-first, local-fallback behavior."""

import json
import random
from typing import Dict, List, Optional

from .client import LLMClient, LLMError
from .models import NPC, CampaignNote
from .prompts import NPC_PROMPT_TEMPLATE, CAMPAIGN_NOTE_PROMPT_TEMPLATE, FALLBACK_NOTICE


# ---- Local fallback data (deterministic, seeded) ----

_RACES = [
    "Human", "Elf", "Dwarf", "Halfling", "Half-Orc", "Tiefling", "Dragonborn",
    "Gnome", "Half-Elf", "Goliath",
]
_CLASSES = [
    "Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Bard", "Druid",
    "Barbarian", "Paladin", "Sorcerer", "Warlock", "Monk",
]
_ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral",
    "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]

_DESCRIPTORS = {
    "Human": ["hardworking", "curious", "adaptable"],
    "Elf": ["graceful", "keen-eyed", "ancient"],
    "Dwarf": ["sturdy", "bearded", "stoic"],
    "Halfling": ["cheerful", "nimble", "fortunates"],
    "Half-Orc": ["fierce", "strong", "proud"],
    "Tiefling": ["mysterious", "horned", "wary"],
    "Dragonborn": ["scaled", "honorable", "imposing"],
    "Gnome": ["inventive", "small", "cheerful"],
    "Half-Elf": ["charming", "versatile", "observant"],
    "Goliath": ["towering", "resilient", "stoic"],
}

_TRAITS = [
    "speaks in riddles", "always carries a flask", "won't touch metal",
    "whistles when nervous", "collects odd trinkets", "distrusts strangers",
    "tells tall tales", "never removes their hat",
]
_IDEALS = ["freedom", "honor", "knowledge", "wealth", "justice", "power", "peace"]
_BONDS = [
    "owes a debt to the local temple",
    "searching for a lost sibling",
    "protects the village shrine",
    "seeks revenge on a rival guild",
]
_FLAWS = [
    "overconfident", "greedy", "slow to trust", "bad temper", "forgetful",
]


def _seed_for(name: str) -> int:
    return sum(ord(c) for c in name)


def _ability_scores(rng: random.Random) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for ability in ["str", "dex", "con", "int", "wis", "cha"]:
        rolls = [rng.randint(1, 6) for _ in range(4)]
        rolls.remove(min(rolls))
        scores[ability] = sum(rolls)
    return scores


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _fallback_npc(
    name: str, race: str, class_name: str, level: int, alignment: str
) -> NPC:
    rng = random.Random(_seed_for(name))
    abilities = _ability_scores(rng)
    con = abilities["con"]
    hit_points = level * (10 + _modifier(con))
    skills = rng.sample(_TRAITS, k=min(3, len(_TRAITS)))
    equipment = rng.sample(
        ["backpack", "waterskin", "torch", "rope", "rations", "dagger", "coin purse"],
        k=3,
    )
    return NPC(
        name=name,
        race=race,
        class_name=class_name,
        level=level,
        alignment=alignment,
        abilities=abilities,
        hit_points=hit_points,
        armor_class=10 + _modifier(abilities["dex"]),
        speed="30 ft.",
        skills=skills,
        equipment=equipment,
        description=(
            f"A {_rng_descriptor(race, rng)} {level}-level {race.lower()} {class_name.lower()}. "
            f"{name} is {alignment.lower()} and carries themselves with quiet confidence."
        ),
        personality_traits=rng.sample(_TRAITS, k=2),
        ideals=rng.sample(_IDEALS, k=1),
        bonds=rng.sample(_BONDS, k=1),
        flaws=rng.sample(_FLAWS, k=1),
        appearance=f"A {race.lower()} with a practical dress and a {class_name.lower()}'s bearing.",
        source="local",
    )


def _rng_descriptor(race: str, rng: random.Random) -> str:
    options = _DESCRIPTORS.get(race, ["capable"])
    return rng.choice(options)


def _fallback_campaign_note(
    title: str, content: str, date: str, tags: List[str]
) -> CampaignNote:
    rng = random.Random(_seed_for(title))
    return CampaignNote(
        title=title,
        content=content,
        date=date,
        tags=tags or ["session"],
        npcs=[],
        locations=["the roadside"],
        plot_hooks=[
            "A mysterious figure watches from the shadows.",
            "An old map surfaced in a merchant's crate.",
        ],
        source="local",
    )


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    # Strip accidental markdown fences if the model added them anyway.
    if text.startswith("```"):
        text = text.split("```", 2)[-1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip("` \n")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in: {text[:120]!r}")
    return json.loads(text[start : end + 1])


class NPCGenerator:
    """Generate NPCs via the LLM, falling back to local templates."""

    def __init__(self, client: Optional[LLMClient] = None) -> None:
        self.client = client or LLMClient()

    def generate(
        self,
        name: str = "Aldric",
        race: str = "Human",
        class_name: str = "Fighter",
        level: int = 1,
        alignment: str = "Neutral Good",
        use_llm: bool = True,
    ) -> NPC:
        if use_llm and self.client is not None:
            try:
                prompt = NPC_PROMPT_TEMPLATE.format(
                    name=name, race=race, class_name=class_name,
                    level=level, alignment=alignment,
                )
                text = self.client.generate(
                    prompt, system_prompt=prompts_system_prompt(), max_tokens=700
                )
                data = _parse_json_object(text)
                return NPC(
                    name=data.get("name", name),
                    race=data.get("race", race),
                    class_name=data.get("class_name", class_name),
                    level=int(data.get("level", level)),
                    alignment=data.get("alignment", alignment),
                    abilities=data.get("abilities", {}),
                    hit_points=int(data.get("hit_points", 0)),
                    armor_class=int(data.get("armor_class", 10)),
                    speed=str(data.get("speed", "30 ft.")),
                    skills=list(data.get("skills", [])),
                    equipment=list(data.get("equipment", [])),
                    description=str(data.get("description", "")),
                    personality_traits=list(data.get("personality_traits", [])),
                    ideals=list(data.get("ideals", [])),
                    bonds=list(data.get("bonds", [])),
                    flaws=list(data.get("flaws", [])),
                    appearance=str(data.get("appearance", "")),
                    source="llm",
                )
            except (LLMError, ValueError, KeyError, TypeError):
                pass
        npc = _fallback_npc(name, race, class_name, level, alignment)
        npc.description += f" {FALLBACK_NOTICE}"
        return npc


class CampaignNoteGenerator:
    """Generate campaign notes via the LLM, falling back to local templates."""

    def __init__(self, client: Optional[LLMClient] = None) -> None:
        self.client = client or LLMClient()

    def generate(
        self,
        title: str = "Session Notes",
        content: str = "The party met at the tavern.",
        date: str = "",
        tags: Optional[List[str]] = None,
        use_llm: bool = True,
    ) -> CampaignNote:
        tags = tags or []
        if not date:
            from datetime import datetime, timezone

            date = datetime.now(timezone.utc).date().isoformat()
        if use_llm and self.client is not None:
            try:
                prompt = CAMPAIGN_NOTE_PROMPT_TEMPLATE.format(
                    title=title, content=content, date=date, tags=", ".join(tags),
                )
                text = self.client.generate(
                    prompt, system_prompt=prompts_system_prompt(), max_tokens=700
                )
                data = _parse_json_object(text)
                return CampaignNote(
                    title=str(data.get("title", title)),
                    content=str(data.get("content", content)),
                    date=str(data.get("date", date)),
                    tags=list(data.get("tags", tags)),
                    npcs=list(data.get("npcs", [])),
                    locations=list(data.get("locations", [])),
                    plot_hooks=list(data.get("plot_hooks", [])),
                    source="llm",
                )
            except (LLMError, ValueError, KeyError, TypeError):
                pass
        note = _fallback_campaign_note(title, content, date, tags)
        note.content += f"\n\n{FALLBACK_NOTICE}"
        return note


def prompts_system_prompt() -> str:
    from .prompts import SYSTEM_PROMPT

    return SYSTEM_PROMPT
