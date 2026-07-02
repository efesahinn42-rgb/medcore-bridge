from uuid import UUID

from app.db.pool import get_pool
from app.services.llm import get_embedding_provider
from app.services.rag.chunking import chunk_text
from app.services.rag.vector_utils import to_pgvector_literal


async def ingest_document(clinic_id: UUID, source_document: str, text: str) -> int:
    """Klinik dokümanını (SSS/fiyat/süreç) parçalayıp embed eder, pgvector'e yazar.

    Aynı kliniğin aynı source_document'ı ile daha önce yüklenmiş parçaları siler —
    tekrar yükleme (doküman güncellemesi) idempotent olsun diye.
    """
    chunks = chunk_text(text)
    embedder = get_embedding_provider()

    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "delete from embeddings where clinic_id = $1 and source_document = $2",
            clinic_id,
            source_document,
        )
        for chunk in chunks:
            vector = await embedder.embed(chunk)
            await conn.execute(
                "insert into embeddings (clinic_id, source_document, content, embedding) "
                "values ($1, $2, $3, $4::vector)",
                clinic_id,
                source_document,
                chunk,
                to_pgvector_literal(vector),
            )

    return len(chunks)
