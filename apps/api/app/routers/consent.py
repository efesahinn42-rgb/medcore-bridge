from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.db.pool import get_pool

router = APIRouter(prefix="/clinics/{clinic_id}", tags=["consent"])

CONSENT_TEXT_VERSION = "v1"


class ConsentRequest(BaseModel):
    consent_given: bool
    language: str


class ConsentResponse(BaseModel):
    user_id: UUID
    conversation_id: UUID | None


@router.post("/consent", response_model=ConsentResponse)
async def give_consent(
    clinic_id: UUID, body: ConsentRequest, request: Request
) -> ConsentResponse:
    """Rıza olmadan konuşma başlamaz (bkz. MedCoreBridge.md §1, katman 1) — consent_given=False
    ise sadece reddi loglar, conversation açmaz."""
    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        user_id = await conn.fetchval(
            "insert into users (clinic_id, channel, preferred_language) "
            "values ($1, 'web_widget', $2) returning id",
            clinic_id,
            body.language,
        )
        await conn.execute(
            "insert into consent_logs "
            "(clinic_id, user_id, consent_given, consent_text_version, language, "
            "ip_address, user_agent) values ($1, $2, $3, $4, $5, $6, $7)",
            clinic_id,
            user_id,
            body.consent_given,
            CONSENT_TEXT_VERSION,
            body.language,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        )

        conversation_id = None
        if body.consent_given:
            conversation_id = await conn.fetchval(
                "insert into conversations (clinic_id, user_id, channel, language) "
                "values ($1, $2, 'web_widget', $3) returning id",
                clinic_id,
                user_id,
                body.language,
            )

    return ConsentResponse(user_id=user_id, conversation_id=conversation_id)
