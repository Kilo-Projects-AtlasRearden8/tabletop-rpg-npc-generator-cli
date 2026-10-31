"""Tests for the LLM client (mock endpoint, no keys)."""

import json
from unittest.mock import patch

import pytest
import requests

from rpg_cli.client import LLMClient, LLMError


def test_generate_returns_content(mock_post, llm_client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "Hello, world"}}]
    }
    result = llm_client.generate("Say hello")
    assert result == "Hello, world"
    # Verify the request was an OpenAI-compatible POST with no api key auth header.
    _, kwargs = mock_post.call_args
    assert "Authorization" not in kwargs["headers"]
    payload = kwargs["json"]
    assert payload["model"] == "llama3"
    assert payload["messages"][0]["content"] == "Say hello"


def test_generate_uses_api_key_when_provided(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }
    client = LLMClient(
        base_url="http://localhost:11434/v1", model="llama3", api_key="test-key"
    )
    client.generate("x")
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"


def test_generate_connection_error_raises(mock_post, llm_client):
    mock_post.side_effect = requests.ConnectionError("refused")
    with pytest.raises(LLMError):
        llm_client.generate("x")


def test_generate_bad_status_raises(mock_post, llm_client):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "boom"
    with pytest.raises(LLMError):
        llm_client.generate("x")


def test_generate_bad_shape_raises(mock_post, llm_client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"not": "choices"}
    with pytest.raises(LLMError):
        llm_client.generate("x")
