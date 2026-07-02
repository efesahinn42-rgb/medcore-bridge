from uuid import UUID

import httpx
import trafilatura

from app.services.rag.ingest import ingest_document

_TIMEOUT = 15.0
_USER_AGENT = "MedCoreBridge-Ingest/1.0 (+https://medcorebridge.example)"


async def ingest_from_url(clinic_id: UUID, url: str) -> int:
    """Klinik web sitesindeki bir sayfayı çekip nav/footer gürültüsünü ayıklayarak
    (trafilatura) ana içeriği pgvector'e ingest eder. Kaynak adı olarak URL kullanılır —
    aynı URL tekrar çekilirse eski chunk'lar silinip yenisiyle değiştirilir."""
    async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": _USER_AGENT})
        response.raise_for_status()

    text = trafilatura.extract(response.text, url=url, favor_recall=True)
    if not text or not text.strip():
        raise ValueError(f"Sayfadan metin çıkarılamadı: {url}")

    return await ingest_document(clinic_id, url, text)
