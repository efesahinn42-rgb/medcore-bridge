import os

import asyncpg
import pytest

from app.services.rag import answer_question, ingest_document
from app.services.rag.chunking import chunk_text

FAQ_DOCUMENT = """Saç ekimi fiyatlarımız 1500 dolardan başlamaktadır, greft sayısına göre değişir.

Klinigimiz hafta içi 09:00-18:00 arası, cumartesi 10:00-14:00 arası hizmet vermektedir.

Saç ekimi sonrası ilk yıkama işlemi klinikte, uzman ekibimiz tarafından yapılır. İyileşme
süreci ortalama 10-14 gün sürer."""


def test_chunk_text_respects_paragraph_boundaries() -> None:
    chunks = chunk_text("Birinci paragraf.\n\nİkinci paragraf.", max_chars=1000)
    assert chunks == ["Birinci paragraf.\n\nİkinci paragraf."]


def test_chunk_text_splits_oversized_paragraph() -> None:
    long_paragraph = "a" * 2500
    chunks = chunk_text(long_paragraph, max_chars=1000)
    assert len(chunks) == 3
    assert all(len(c) <= 1000 for c in chunks)
    assert "".join(chunks) == long_paragraph


@pytest.fixture
async def clinic_id():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    clinic_id = await conn.fetchval(
        "insert into clinics (name, slug) values ("
        "'RAG Test Klinik', 'rag-test-' || substr(gen_random_uuid()::text, 1, 8)"
        ") returning id"
    )
    yield clinic_id
    await conn.execute("delete from clinics where id = $1", clinic_id)
    await conn.close()


async def test_ingest_and_answer_grounded_question(clinic_id) -> None:
    chunk_count = await ingest_document(clinic_id, "faq.txt", FAQ_DOCUMENT)
    assert (
        chunk_count == 1
    )  # tüm doküman 1000 karakterin altında, tek chunk'a paketleniyor

    answer = await answer_question(clinic_id, "Saç ekimi fiyatı ne kadar?")
    assert "1500" in answer


async def test_answer_redirects_on_emergency_symptom(clinic_id) -> None:
    await ingest_document(clinic_id, "faq.txt", FAQ_DOCUMENT)

    answer = await answer_question(
        clinic_id, "Göğsümde şiddetli ağrı var, ne yapmalıyım?"
    )
    assert "112" in answer


async def test_answer_does_not_hallucinate_out_of_scope_price(clinic_id) -> None:
    await ingest_document(clinic_id, "faq.txt", FAQ_DOCUMENT)

    answer = await answer_question(clinic_id, "Burun estetiği fiyatınız nedir?")
    assert "1500" not in answer
