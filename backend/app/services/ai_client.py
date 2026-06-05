import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class AiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("MIMO_API_KEY", "")
        self.base_url = os.getenv("MIMO_BASE_URL", "https://api.mimo-v2.com/v1").rstrip("/")
        self.model = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
        self.use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key) and not self.use_mock

    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.35) -> str:
        if not self.enabled:
            raise RuntimeError("AI client is not configured.")

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
