from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.pool import get_pool
from app.services.llm import ChatMessage
from app.services.pii_masking import detokenize_all, mask_text
from app.services.rag import answer_question

router = APIRouter(prefix="/conversations/{conversation_id}", tags=["chat"])

HISTORY_LIMIT = 6


class MessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    role: str
    content: str


@router.post("/messages", response_model=MessageResponse)
async def send_message(conversation_id: UUID, body: MessageRequest) -> MessageResponse:
    pool = await get_pool()

    async with pool.acquire() as conn:
        conversation = await conn.fetchrow(
            "select clinic_id, status from conversations where id = $1", conversation_id
        )
        if conversation is None:
            raise HTTPException(status_code=404, detail="conversation not found")
        if conversation["status"] != "active":
            raise HTTPException(status_code=409, detail="conversation is not active")

        history_rows = await conn.fetch(
            "select role, content from messages where conversation_id = $1 "
            "order by created_at desc limit $2",
            conversation_id,
            HISTORY_LIMIT,
        )
        await conn.execute(
            "insert into messages (conversation_id, role, content) values ($1, 'user', $2)",
            conversation_id,
            body.content,
        )

    # LLM'e giden her şey maskeli: geçmişteki hasta mesajları + şu anki soru.
    # Asistan mesajları zaten RAG bağlamından üretiliyor, PII içermez — maskelenmez.
    history = [
        ChatMessage(
            role=row["role"],
            content=(await mask_text(conversation_id, row["content"]))
            if row["role"] == "user"
            else row["content"],
        )
        for row in reversed(history_rows)
    ]
    masked_question = await mask_text(conversation_id, body.content)

    raw_answer = await answer_question(
        conversation["clinic_id"], masked_question, history=history
    )
    answer = await detokenize_all(conversation_id, raw_answer)

    async with pool.acquire() as conn:
        await conn.execute(
            "insert into messages (conversation_id, role, content, llm_provider) "
            "values ($1, 'assistant', $2, $3)",
            conversation_id,
            answer,
            get_settings().llm_provider,
        )

    return MessageResponse(role="assistant", content=answer)
