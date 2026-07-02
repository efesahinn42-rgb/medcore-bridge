from typing import Protocol


class ChatMessage:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class ChatProvider(Protocol):
    """Claude/Gemini/OpenAI — hangisi aktifse aynı arayüzden çağrılır (bkz. provider.py)."""

    async def complete(self, system: str, messages: list[ChatMessage]) -> str: ...


class EmbeddingProvider(Protocol):
    async def embed(self, text: str, dimensions: int = 1536) -> list[float]: ...
