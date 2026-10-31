"""Shared fixtures for rpg_cli tests."""

from typing import Any, Dict
from unittest.mock import patch

import pytest

from rpg_cli.client import LLMClient
from rpg_cli.generator import NPCGenerator, CampaignNoteGenerator


class MockResponse:
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self._json = json_data
        self.status_code = status_code
        self.text = ""

    def json(self) -> Dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def mock_post():
    """Patch requests.post so tests never touch the network."""
    with patch("rpg_cli.client.requests.post") as m:
        yield m


@pytest.fixture
def llm_client():
    return LLMClient(base_url="http://localhost:11434/v1", model="llama3")


@pytest.fixture
def npc_generator(llm_client):
    return NPCGenerator(client=llm_client)


@pytest.fixture
def note_generator(llm_client):
    return CampaignNoteGenerator(client=llm_client)


def mock_chat_response(text: str) -> Dict[str, Any]:
    return {"choices": [{"message": {"content": text}}]}
