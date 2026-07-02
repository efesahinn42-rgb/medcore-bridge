from functools import lru_cache
from uuid import UUID

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider

from app.services.pii_masking.recognizers import get_custom_recognizers
from app.services.pii_masking.vault import tokenize

SUPPORTED_ENTITIES = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "TR_ID_NUMBER",
    "PASSPORT",
]


@lru_cache
def get_analyzer() -> AnalyzerEngine:
    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
    )
    analyzer = AnalyzerEngine(
        nlp_engine=provider.create_engine(), supported_languages=["en"]
    )
    for recognizer in get_custom_recognizers():
        analyzer.registry.add_recognizer(recognizer)
    return analyzer


def _select_non_overlapping(results: list[RecognizerResult]) -> list[RecognizerResult]:
    chosen: list[RecognizerResult] = []
    for result in sorted(results, key=lambda r: r.score, reverse=True):
        if any(result.start < c.end and c.start < result.end for c in chosen):
            continue
        chosen.append(result)
    return sorted(chosen, key=lambda r: r.start)


async def mask_text(conversation_id: UUID, text: str) -> str:
    """PII'yi tespit edip [HASTA_A] gibi token'larla değiştirir; gerçek değer vault'a yazılır."""
    results = get_analyzer().analyze(
        text=text, language="en", entities=SUPPORTED_ENTITIES
    )
    spans = _select_non_overlapping(results)

    masked = text
    for span in reversed(spans):
        real_value = text[span.start : span.end]
        token = await tokenize(conversation_id, span.entity_type, real_value)
        masked = masked[: span.start] + token + masked[span.end :]
    return masked
