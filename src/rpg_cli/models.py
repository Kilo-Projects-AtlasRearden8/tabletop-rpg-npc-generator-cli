"""Data models for NPCs and campaign notes."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NPC:
    """A tabletop RPG non-player character."""

    name: str
    race: str
    class_name: str
    level: int
    alignment: str
    abilities: Dict[str, int] = field(default_factory=dict)
    hit_points: int = 0
    armor_class: int = 10
    speed: str = "30 ft."
    skills: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    description: str = ""
    personality_traits: List[str] = field(default_factory=list)
    ideals: List[str] = field(default_factory=list)
    bonds: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)
    appearance: str = ""
    source: str = "local"
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CampaignNote:
    """A campaign note / session log entry."""

    title: str
    content: str
    date: str = field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
    tags: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    plot_hooks: List[str] = field(default_factory=list)
    source: str = "local"
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)
