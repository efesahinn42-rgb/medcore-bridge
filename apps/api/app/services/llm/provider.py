from functools import lru_cache

from app.core.config import get_settings
from app.services.llm.base import ChatProvider, EmbeddingProvider


def _build_chat_provider(name: str) -> ChatProvider:
    if name == "gemini":
        from app.services.llm.gemini import GeminiProvider

        return GeminiProvider()
    if name == "claude":
        from app.services.llm.claude import ClaudeProvider

        return ClaudeProvider()
    if name == "groq":
        from app.services.llm.groq_provider import GroqProvider

        return GroqProvider()
    raise ValueError(f"Unknown LLM provider: {name}")


@lru_cache
def get_chat_provider() -> ChatProvider:
    settings = get_settings()
    primary = _build_chat_provider(settings.llm_provider)

    fallback_name = settings.llm_fallback_provider
    if not fallback_name or fallback_name == settings.llm_provider:
        return primary

    from app.services.llm.failover import FailoverChatProvider

    return FailoverChatProvider(primary, lambda: _build_chat_provider(fallback_name))


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Claude ve Groq'ta embedding API'si yok — RAG her zaman Gemini üzerinden embed eder."""
    from app.services.llm.gemini import GeminiProvider

    return GeminiProvider()
