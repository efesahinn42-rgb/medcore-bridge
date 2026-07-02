from groq import AsyncGroq

from app.core.config import get_settings
from app.services.llm.base import ChatMessage

# Gemini'nin ücretsiz kotasına yedek — llama-3.3-70b günde 1000 istek/ücretsiz,
# OpenAI-uyumlu API. Groq'ta embedding/vision yok — sadece metin sohbeti için.
MODEL = "llama-3.3-70b-versatile"


class GroqProvider:
    def __init__(self) -> None:
        api_key = get_settings().groq_api_key
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        self._client = AsyncGroq(api_key=api_key)

    async def complete(self, system: str, messages: list[ChatMessage]) -> str:
        response = await self._client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                *({"role": m.role, "content": m.content} for m in messages),
            ],
        )
        return response.choices[0].message.content
