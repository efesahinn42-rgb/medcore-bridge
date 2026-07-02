import pytest

from app.services.llm import ChatMessage, get_chat_provider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.provider import get_chat_provider as _get_chat_provider


def test_default_provider_is_gemini() -> None:
    get_chat_provider.cache_clear()
    provider = get_chat_provider()
    assert isinstance(provider, GeminiProvider)


def test_unknown_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.config import get_settings

    get_settings.cache_clear()
    _get_chat_provider.cache_clear()
    monkeypatch.setenv("LLM_PROVIDER", "not-a-real-provider")
    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        _get_chat_provider()
    get_settings.cache_clear()
    _get_chat_provider.cache_clear()


async def test_gemini_completes_a_simple_prompt() -> None:
    get_chat_provider.cache_clear()
    provider = get_chat_provider()
    answer = await provider.complete(
        system="Sadece rakamla cevap ver, başka hiçbir şey yazma.",
        messages=[ChatMessage(role="user", content="2+2 kactir?")],
    )
    assert "4" in answer
