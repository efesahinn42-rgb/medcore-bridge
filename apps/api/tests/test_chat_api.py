import os

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.rag import ingest_document

FAQ_DOCUMENT = (
    "Diş implant fiyatlarımız 400 dolardan başlamaktadır. "
    "Kliniğimiz hafta içi 09:00-18:00 arası hizmet vermektedir."
)


@pytest.fixture
async def clinic_id():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    clinic_id = await conn.fetchval(
        "insert into clinics (name, slug) values ("
        "'Chat API Test Klinik', 'chat-api-test-' || substr(gen_random_uuid()::text, 1, 8)"
        ") returning id"
    )
    yield clinic_id
    await conn.execute("delete from clinics where id = $1", clinic_id)
    await conn.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_consent_given_creates_conversation(
    clinic_id, client: AsyncClient
) -> None:
    resp = await client.post(
        f"/clinics/{clinic_id}/consent", json={"consent_given": True, "language": "tr"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"]
    assert body["conversation_id"]


async def test_consent_refused_does_not_create_conversation(
    clinic_id, client: AsyncClient
) -> None:
    resp = await client.post(
        f"/clinics/{clinic_id}/consent", json={"consent_given": False, "language": "tr"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_id"]
    assert body["conversation_id"] is None


async def test_chat_end_to_end_via_api(clinic_id, client: AsyncClient) -> None:
    await ingest_document(clinic_id, "faq.txt", FAQ_DOCUMENT)

    consent_resp = await client.post(
        f"/clinics/{clinic_id}/consent", json={"consent_given": True, "language": "tr"}
    )
    conversation_id = consent_resp.json()["conversation_id"]

    resp = await client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content": "Diş implant fiyatı ne kadar?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "assistant"
    assert "400" in body["content"]


async def test_chat_on_unknown_conversation_returns_404(client: AsyncClient) -> None:
    resp = await client.post(
        "/conversations/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "Merhaba"},
    )
    assert resp.status_code == 404


async def test_chat_masks_pii_before_sending_to_llm(
    clinic_id, client: AsyncClient
) -> None:
    """Kullanıcı mesajındaki PII, vault'a tokenize edilmiş halde yansımalı — bu test
    conversation'ın consent akışından geçtiğini ve mesajın DB'ye yazıldığını doğrular."""
    await ingest_document(clinic_id, "faq.txt", FAQ_DOCUMENT)
    consent_resp = await client.post(
        f"/clinics/{clinic_id}/consent", json={"consent_given": True, "language": "tr"}
    )
    conversation_id = consent_resp.json()["conversation_id"]

    resp = await client.post(
        f"/conversations/{conversation_id}/messages",
        json={"content": "Ben Ahmet Yilmaz, dis implant fiyati nedir?"},
    )
    assert resp.status_code == 200

    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    vault_row = await conn.fetchrow(
        "select entity_type from pii_vault where conversation_id = $1 and entity_type = 'PERSON'",
        conversation_id,
    )
    await conn.close()
    assert vault_row is not None
