import os

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def clinic_id():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    clinic_id = await conn.fetchval(
        "insert into clinics (name, slug) values ("
        "'Documents API Test Klinik', 'docs-api-test-' || substr(gen_random_uuid()::text, 1, 8)"
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


async def test_ingest_text_endpoint(clinic_id, client: AsyncClient) -> None:
    resp = await client.post(
        f"/clinics/{clinic_id}/documents",
        json={
            "source_document": "manual.txt",
            "content": "Klinigimiz Istanbul Sisli'de bulunmaktadir.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source_document"] == "manual.txt"
    assert body["chunk_count"] == 1


async def test_ingest_from_url_endpoint(clinic_id, client: AsyncClient) -> None:
    resp = await client.post(
        f"/clinics/{clinic_id}/documents/from-url",
        json={"url": "https://example.com"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["chunk_count"] >= 1

    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    row = await conn.fetchrow(
        "select content from embeddings where clinic_id = $1 and source_document = $2",
        clinic_id,
        "https://example.com",
    )
    await conn.close()
    assert row is not None
    assert "example" in row["content"].lower()


async def test_ingest_from_url_with_bad_url_returns_502(
    clinic_id, client: AsyncClient
) -> None:
    resp = await client.post(
        f"/clinics/{clinic_id}/documents/from-url",
        json={"url": "https://this-domain-does-not-exist-medcorebridge-test.invalid"},
    )
    assert resp.status_code == 502
