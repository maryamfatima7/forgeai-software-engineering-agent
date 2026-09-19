import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.core.errors import ForgeAIError


@dataclass(frozen=True)
class LLMRequest:
    system_instruction: str
    prompt: str


@dataclass(frozen=True)
class LLMResponse:
    content: str


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not settings.gemini_api_key:
            raise ForgeAIError("llm_not_configured", "GEMINI_API_KEY is not configured for this deployment.", 503)
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": request.system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": request.prompt[:settings.max_context_characters]}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2_000},
        }
        try:
            async with httpx.AsyncClient(timeout=settings.gemini_timeout_seconds) as client:
                response = await client.post(endpoint, params={"key": settings.gemini_api_key}, json=payload)
                response.raise_for_status()
                data = response.json()
            return LLMResponse(content=data["candidates"][0]["content"]["parts"][0]["text"])
        except (httpx.TimeoutException, httpx.HTTPStatusError) as error:
            raise ForgeAIError("llm_unavailable", "The configured LLM provider could not complete the request.", 502) from error
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise ForgeAIError("llm_invalid_response", "The LLM provider returned an unusable response.", 502) from error


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider.lower() == "gemini":
        return GeminiProvider()
    raise ForgeAIError("unsupported_llm_provider", f"Unsupported LLM provider: {settings.llm_provider}", 500)
