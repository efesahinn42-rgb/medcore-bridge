from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.llm.base import ChatMessage

_ROLE_MAP = {"user": "user", "assistant": "model"}

# flash-lite: ücretsiz katmanda flash'tan belirgin şekilde daha yüksek günlük kota
# (bkz. medcorebridge_project memory notu — flash'ın gerçek gözlemlenen limiti günde 20 istekti)
CHAT_MODEL = "gemini-2.5-flash-lite"


class GeminiProvider:
    def __init__(self) -> None:
        api_key = get_settings().gemini_api_key
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self._client = genai.Client(api_key=api_key)

    async def complete(self, system: str, messages: list[ChatMessage]) -> str:
        contents = [
            types.Content(role=_ROLE_MAP[m.role], parts=[types.Part(text=m.content)])
            for m in messages
        ]
        response = await self._client.aio.models.generate_content(
            model=CHAT_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return response.text

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        response = await self._client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=dimensions),
        )
        return response.embeddings[0].values
