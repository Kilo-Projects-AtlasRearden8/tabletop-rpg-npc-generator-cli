"""Prompt templates for NPC and campaign note generation."""

SYSTEM_PROMPT = (
    "You are a helpful tabletop RPG assistant. Generate clear, usable, "
    "printable NPC and campaign note content. Return only the requested "
    "structured text, no conversational filler."
)

NPC_PROMPT_TEMPLATE = """Generate a tabletop RPG non-player character (NPC) with the following details:
- Name: {name}
- Race: {race}
- Class: {class_name}
- Level: {level}
- Alignment: {alignment}

Return the result as a JSON object with exactly these keys:
name, race, class_name, level, alignment, abilities (object with str/dex/con/int/wis/cha scores 3-18),
hit_points (integer), armor_class (integer), speed (string), skills (list of strings),
equipment (list of strings), description (string), personality_traits (list of strings),
ideals (list of strings), bonds (list of strings), flaws (list of strings), appearance (string).

Return valid JSON only, no markdown code fences, no extra text."""

CAMPAIGN_NOTE_PROMPT_TEMPLATE = """Generate a tabletop RPG campaign note with the following details:
- Title: {title}
- Content summary: {content}
- Date: {date}
- Tags: {tags}

Return the result as a JSON object with exactly these keys:
title, content, date, tags (list of strings), npcs (list of strings),
locations (list of strings), plot_hooks (list of strings).

Return valid JSON only, no markdown code fences, no extra text."""

FALLBACK_NOTICE = "(generated locally - no LLM endpoint reachable)"
