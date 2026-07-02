from uuid import UUID

from app.db.pool import get_pool
from app.services.llm import ChatMessage, get_chat_provider, get_embedding_provider
from app.services.rag.vector_utils import to_pgvector_literal

TOP_K = 4

# Bkz. MedCoreBridge.md §2 — "Bilgilendirme + Ön Triyaj" konumlandırması, sistem promptuna
# gömülmesi gereken kurallar burada birebir uygulanıyor.
SYSTEM_PROMPT = """Sen bir sağlık turizmi kliniğinin bilgilendirme ve ön triyaj asistanısın.

KURALLAR (kesinlikle uy):
- Yalnızca aşağıdaki BAĞLAM'da verilen bilgilere dayanarak yanıt ver. Bağlamda olmayan hiçbir
  tıbbi veya finansal iddiada bulunma; kaynaksız bilgi üretme.
- Bağlamda sorunun cevabı yoksa açıkça söyle: "Bu konuda elimde bilgi yok, sizi kliniğe
  yönlendireyim." Tahmin yürütme.
- Teşhis koyma, ilaç/doz önerme veya reçete yazma isteği gelirse nazikçe reddet ve hastayı
  hekime/insan temsilciye yönlendir.
- Acil belirti (göğüs ağrısı, ciddi kanama, nefes darlığı, bilinç kaybı vb.) belirtilirse
  başka hiçbir şey söylemeden anında "112'yi arayın veya en yakın acil servise gidin" de.
- Yanıtın sonuna kısa bir sorumluluk reddi ekle: "Bu bilgi genel bilgilendirme amaçlıdır;
  tıbbi teşhis/tedavi yerine geçmez."

BAĞLAM:
{context}
"""


async def answer_question(
    clinic_id: UUID, question: str, history: list[ChatMessage] | None = None
) -> str:
    """history verilirse (önceki tur(lar)ı), çok turlu bağlamla yanıtlar — RAG araması
    yine sadece en son soruya göre yapılır, önceki turlar sadece sohbet bağlamı sağlar."""
    embedder = get_embedding_provider()
    question_vector = await embedder.embed(question)
    vector_literal = to_pgvector_literal(question_vector)

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "select content from embeddings where clinic_id = $1 "
            "order by embedding <=> $2::vector limit $3",
            clinic_id,
            vector_literal,
            TOP_K,
        )

    context = (
        "\n\n---\n\n".join(row["content"] for row in rows)
        if rows
        else "(bilgi tabanı boş)"
    )
    system = SYSTEM_PROMPT.format(context=context)

    chat = get_chat_provider()
    messages = [*(history or []), ChatMessage(role="user", content=question)]
    return await chat.complete(system=system, messages=messages)
