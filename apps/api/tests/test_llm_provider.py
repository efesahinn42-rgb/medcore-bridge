import pytest

from app.services.llm import ChatMessage, get_chat_provider
from app.services.llm.failover import FailoverChatProvider
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.provider import get_chat_provider as _get_chat_provider


def test_default_provider_has_groq_fallback() -> None:
    """LLM_FALLBACK_PROVIDER=groq varsayılan — Gemini kota/hata verirse otomatik düşer."""
    get_chat_provider.cache_clear()
    provider = get_chat_provider()
    assert isinstance(provider, FailoverChatProvider)


def test_unknown_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.config import get_settings

    get_settings.cache_clear()
    _get_chat_provider.cache_clear()
    monkeypatch.setenv("LLM_PROVIDER", "not-a-real-provider")
    with pytest.raises(ValueError, match="Unknown LLM provider"):
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


async def test_groq_completes_a_simple_prompt() -> None:
    provider = GroqProvider()
    answer = await provider.complete(
        system="Sadece rakamla cevap ver, başka hiçbir şey yazma.",
        messages=[ChatMessage(role="user", content="3+3 kactir?")],
    )
    assert "6" in answer


async def test_failover_falls_back_when_primary_fails() -> None:
    class BrokenProvider:
        async def complete(self, system: str, messages: list[ChatMessage]) -> str:
            raise RuntimeError("simulated outage")

    provider = FailoverChatProvider(BrokenProvider(), lambda: GroqProvider())
    answer = await provider.complete(
        system="Sadece rakamla cevap ver, başka hiçbir şey yazma.",
        messages=[ChatMessage(role="user", content="5+5 kactir?")],
    )
    assert "10" in answer
