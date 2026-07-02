import logging
from collections.abc import Callable

from app.services.llm.base import ChatMessage, ChatProvider

logger = logging.getLogger(__name__)


class FailoverChatProvider:
    """Birincil sağlayıcı hata verirse (kota/429/503 vb.) otomatik ikinciye düşer.

    fallback_factory lazy'dir — fallback sağlayıcı sadece gerçekten gerektiğinde
    kurulur (ör. GROQ_API_KEY tanımsızsa ve Gemini hiç hata vermiyorsa hiç sorun çıkmaz).
    """

    def __init__(
        self, primary: ChatProvider, fallback_factory: Callable[[], ChatProvider]
    ) -> None:
        self._primary = primary
        self._fallback_factory = fallback_factory

    async def complete(self, system: str, messages: list[ChatMessage]) -> str:
        try:
            return await self._primary.complete(system, messages)
        except Exception:
            logger.warning("Primary LLM provider failed, falling back", exc_info=True)
            fallback = self._fallback_factory()
            return await fallback.complete(system, messages)
