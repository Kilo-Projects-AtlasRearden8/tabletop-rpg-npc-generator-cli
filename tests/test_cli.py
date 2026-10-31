"""Tests for the CLI (argparse-based)."""

import io
import json
from contextlib import redirect_stdout

import pytest

from rpg_cli.cli import main


def _run(args):
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = main(args)
    except SystemExit as e:
        code = e.code if e.code is not None else 2
    return code, buf.getvalue()


def test_cli_npc_prints_markdown():
    code, out = _run(["npc", "--name", "Testo", "--no-llm"])
    assert code == 0
    assert "# Testo" in out


def test_cli_note_prints_markdown():
    code, out = _run(["note", "--title", "My Note", "--no-llm"])
    assert code == 0
    assert "# My Note" in out


def test_cli_json_output():
    code, out = _run(["npc", "--name", "J", "--format", "json", "--no-llm"])
    assert code == 0
    data = json.loads(out)
    assert data["name"] == "J"


def test_cli_missing_command_errors():
    code, out = _run([])
    assert code != 0


def test_cli_unknown_flag_errors():
    code, out = _run(["npc", "--bogus", "x"])
    assert code != 0
