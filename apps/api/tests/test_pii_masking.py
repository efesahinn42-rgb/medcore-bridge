import os

import asyncpg
import pytest

from app.services.pii_masking.crypto import decrypt, encrypt
from app.services.pii_masking.mask import mask_text
from app.services.pii_masking.recognizers import _tc_kimlik_checksum_valid
from app.services.pii_masking.vault import detokenize_all, tokenize

# "12345678950" algoritmayla üretilmiş geçerli-checksum'lı bir örnektir, gerçek bir kimlik
# numarası değildir (d1..d9 = 123456789, d10/d11 checksum formülünden hesaplandı).
VALID_TC = "12345678950"


def test_crypto_roundtrip() -> None:
    ciphertext = encrypt("Ahmet Yılmaz")
    assert ciphertext != b"Ahmet Y\xc4\xb1lmaz"
    assert decrypt(ciphertext) == "Ahmet Yılmaz"


def test_crypto_tamper_detection() -> None:
    tampered = bytearray(encrypt("secret"))
    tampered[-1] ^= 0xFF
    with pytest.raises(Exception):
        decrypt(bytes(tampered))


@pytest.mark.parametrize(
    ("tc", "expected"),
    [
        (VALID_TC, True),
        ("12345678901", False),  # checksum tutmuyor
        ("00000000000", False),  # ilk hane 0 olamaz
    ],
)
def test_tc_kimlik_checksum(tc: str, expected: bool) -> None:
    assert _tc_kimlik_checksum_valid(tc) == expected


@pytest.fixture
async def conversation_id():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])
    clinic_id = await conn.fetchval(
        "insert into clinics (name, slug) values ("
        "'PII Test Klinik', 'pii-test-' || substr(gen_random_uuid()::text, 1, 8)"
        ") returning id"
    )
    user_id = await conn.fetchval(
        "insert into users (clinic_id, channel) values ($1, 'web_widget') returning id",
        clinic_id,
    )
    conv_id = await conn.fetchval(
        "insert into conversations (clinic_id, user_id, channel) "
        "values ($1, $2, 'web_widget') returning id",
        clinic_id,
        user_id,
    )
    yield conv_id
    await conn.execute("delete from clinics where id = $1", clinic_id)
    await conn.close()


async def test_mask_and_detokenize_roundtrip(conversation_id) -> None:
    text = "Merhaba, adim Ahmet Yilmaz, telefonum +905551234567."
    masked = await mask_text(conversation_id, text)

    assert "Ahmet Yilmaz" not in masked
    assert "+905551234567" not in masked
    assert "[HASTA_A]" in masked

    restored = await detokenize_all(conversation_id, masked)
    assert restored == text


async def test_tokenize_reuses_same_token_for_same_value(conversation_id) -> None:
    """Vault seviyesinde token yeniden-kullanımı — NER tutarlılığından bağımsız.

    Not: mask_text uçtan uca testinde aynı ismi farklı cümle bağlamlarında birebir
    aynı span olarak tespit etmek spaCy'nin (özellikle küçük modelin) NER
    tutarlılığına bağlıdır ve garanti değildir; bu yüzden reuse mantığı burada
    vault.tokenize() üzerinden doğrudan test ediliyor.
    """
    first = await tokenize(conversation_id, "PERSON", "Ahmet Yilmaz")
    second = await tokenize(conversation_id, "PERSON", "Ahmet Yilmaz")
    assert first == second == "[HASTA_A]"

    third = await tokenize(conversation_id, "PERSON", "Mehmet Demir")
    assert third == "[HASTA_B]"
