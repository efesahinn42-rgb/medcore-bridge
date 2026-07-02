from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag import ingest_document, ingest_from_url

router = APIRouter(prefix="/clinics/{clinic_id}/documents", tags=["documents"])


class IngestTextRequest(BaseModel):
    source_document: str
    content: str


class IngestUrlRequest(BaseModel):
    url: str


class IngestResponse(BaseModel):
    source_document: str
    chunk_count: int


@router.post("", response_model=IngestResponse)
async def ingest_text(clinic_id: UUID, body: IngestTextRequest) -> IngestResponse:
    chunk_count = await ingest_document(clinic_id, body.source_document, body.content)
    return IngestResponse(source_document=body.source_document, chunk_count=chunk_count)


@router.post("/from-url", response_model=IngestResponse)
async def ingest_url(clinic_id: UUID, body: IngestUrlRequest) -> IngestResponse:
    try:
        chunk_count = await ingest_from_url(clinic_id, body.url)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Sayfa alınamadı: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return IngestResponse(source_document=body.url, chunk_count=chunk_count)
