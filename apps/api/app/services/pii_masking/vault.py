import string
from uuid import UUID

from app.db.pool import get_pool
from app.services.pii_masking.crypto import decrypt, encrypt

_TOKEN_LABELS = {
    "PERSON": "HASTA",
    "PHONE_NUMBER": "TELEFON",
    "EMAIL_ADDRESS": "EMAIL",
    "TR_ID_NUMBER": "TC",
    "PASSPORT": "PASAPORT",
}


def _label_for(entity_type: str) -> str:
    return _TOKEN_LABELS.get(entity_type, entity_type)


def _suffix_for(index: int) -> str:
    """0->A, 1->B, ..., 25->Z, 26->AA, ..."""
    letters = string.ascii_uppercase
    result = ""
    index += 1
    while index > 0:
        index, rem = divmod(index - 1, 26)
        result = letters[rem] + result
    return result


async def tokenize(conversation_id: UUID, entity_type: str, real_value: str) -> str:
    """Aynı conversation içinde aynı değer her zaman aynı token'a eşlenir."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            rows = await conn.fetch(
                "select token, encrypted_value from pii_vault "
                "where conversation_id = $1 and entity_type = $2 "
                "order by created_at for update",
                conversation_id,
                entity_type,
            )
            for row in rows:
                if decrypt(bytes(row["encrypted_value"])) == real_value:
                    return row["token"]

            label = _label_for(entity_type)
            token = f"[{label}_{_suffix_for(len(rows))}]"
            await conn.execute(
                "insert into pii_vault (conversation_id, token, entity_type, encrypted_value) "
                "values ($1, $2, $3, $4)",
                conversation_id,
                token,
                entity_type,
                encrypt(real_value),
            )
            return token


async def detokenize_all(conversation_id: UUID, text: str) -> str:
    """Metindeki tüm [TOKEN]'ları gerçek değerleriyle değiştirir (ör. CRM'e göndermeden önce)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "select token, encrypted_value from pii_vault where conversation_id = $1",
            conversation_id,
        )
    for row in rows:
        text = text.replace(row["token"], decrypt(bytes(row["encrypted_value"])))
    return text
