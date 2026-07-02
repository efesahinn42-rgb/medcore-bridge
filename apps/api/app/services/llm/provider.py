from functools import lru_cache

from app.core.config import get_settings
from app.services.llm.base import ChatProvider, EmbeddingProvider


@lru_cache
def get_chat_provider() -> ChatProvider:
    provider = get_settings().llm_provider
    if provider == "gemini":
        from app.services.llm.gemini import GeminiProvider

        return GeminiProvider()
    if provider == "claude":
        from app.services.llm.claude import ClaudeProvider

        return ClaudeProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Claude'un embedding API'si yok — RAG her zaman Gemini üzerinden embed eder,
    LLM_PROVIDER=claude olsa bile (chat ve embedding sağlayıcısı bağımsız seçilir)."""
    from app.services.llm.gemini import GeminiProvider

    return GeminiProvider()
