from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
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
        raise NotImplementedError("Gemini integration is reserved for a future phase.")
