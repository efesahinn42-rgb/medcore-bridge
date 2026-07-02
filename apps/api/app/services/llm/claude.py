from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.services.llm.base import ChatMessage

MODEL = "claude-sonnet-5"


class ClaudeProvider:
    """Faz 1/Hafta 4'ün asıl planı — şu an aktif değil (ANTHROPIC_API_KEY yok),
    key eklenince kodu değiştirmeden LLM_PROVIDER=claude ile devreye girer."""

    def __init__(self) -> None:
        api_key = get_settings().anthropic_api_key
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = AsyncAnthropic(api_key=api_key)

    async def complete(self, system: str, messages: list[ChatMessage]) -> str:
        response = await self._client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return next(block.text for block in response.content if block.type == "text")
