"""Command-line interface for the RPG NPC / campaign note generator."""

import argparse
import json
import sys
from typing import List, Optional

from .client import LLMClient
from .generator import NPCGenerator, CampaignNoteGenerator
from .models import NPC
from .storage import save_markdown, save_json, npc_to_markdown, campaign_note_to_markdown


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rpg",
        description=(
            "Local-first tabletop RPG NPC and campaign note generator. "
            "Defaults to a local Ollama endpoint; falls back to local templates "
            "when no endpoint is reachable."
        ),
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:11434/v1",
        help="OpenAI-compatible endpoint base URL "
        "(default: http://localhost:11434/v1)",
    )
    parser.add_argument(
        "--model", default="llama3", help="Model name (default: llama3)"
    )
    parser.add_argument(
        "--api-key", default=None, help="API key, if the endpoint requires one"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    def _add_output_options(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--format",
            choices=["md", "json"],
            default=None,
            help="Output format (default: md)",
        )
        p.add_argument(
            "--output", "-o", default=None, help="Output file path (default: stdout)"
        )

    # npc
    npc_p = sub.add_parser("npc", help="Generate an NPC")
    npc_p.add_argument("--name", default="Aldric")
    npc_p.add_argument("--race", default="Human")
    npc_p.add_argument("--class", dest="class_name", default="Fighter")
    npc_p.add_argument("--level", type=int, default=1)
    npc_p.add_argument("--alignment", default="Neutral Good")
    npc_p.add_argument(
        "--no-llm", action="store_true",
        help="Skip the LLM and use local templates only",
    )
    _add_output_options(npc_p)

    # note
    note_p = sub.add_parser("note", help="Generate a campaign note")
    note_p.add_argument("--title", default="Session Notes")
    note_p.add_argument("--content", default="The party met at the tavern.")
    note_p.add_argument("--date", default="")
    note_p.add_argument("--tag", action="append", default=[], help="Add a tag")
    note_p.add_argument(
        "--no-llm", action="store_true",
        help="Skip the LLM and use local templates only",
    )
    _add_output_options(note_p)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse calls sys.exit(2) on usage errors; surface as a return code.
        return int(exc.code) if exc.code is not None else 2

    client = LLMClient(base_url=args.endpoint, model=args.model, api_key=args.api_key)
    npc_gen = NPCGenerator(client=client)
    note_gen = CampaignNoteGenerator(client=client)

    if args.command == "npc":
        obj = npc_gen.generate(
            name=args.name,
            race=args.race,
            class_name=args.class_name,
            level=args.level,
            alignment=args.alignment,
            use_llm=not args.no_llm,
        )
    else:  # note
        obj = note_gen.generate(
            title=args.title,
            content=args.content,
            date=args.date,
            tags=args.tag,
            use_llm=not args.no_llm,
        )

    fmt = args.format or "md"
    if fmt == "json":
        text = json.dumps(obj.to_dict(), indent=2, ensure_ascii=False)
    else:
        if isinstance(obj, NPC):
            text = npc_to_markdown(obj)
        else:
            text = campaign_note_to_markdown(obj)

    if args.output:
        if fmt == "json":
            save_json(obj, args.output)
        else:
            save_markdown(obj, args.output)
        print(f"Saved {args.command} to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
