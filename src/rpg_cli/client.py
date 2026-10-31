"""LLM client for OpenAI-compatible endpoints (default Ollama)."""

from typing import List, Dict, Optional
import requests


class LLMError(Exception):
    """Raised when the LLM endpoint cannot be reached or returns an error."""


class LLMClient:
    """Thin client over an OpenAI-compatible chat/completions endpoint.

    Defaults to Ollama running locally at http://localhost:11434/v1.
    No API key is required by default.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "llama3",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            response = requests.post(
                url, headers=self._headers(), json=payload, timeout=self.timeout
            )
        except requests.RequestException as exc:  # connection refused, DNS, etc.
            raise LLMError(f"Could not reach endpoint {url}: {exc}") from exc

        if response.status_code >= 400:
            raise LLMError(
                f"Endpoint returned {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected response shape: {data!r}") from exc

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.chat(
            messages, temperature=temperature, max_tokens=max_tokens
        )
