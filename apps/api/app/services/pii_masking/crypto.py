import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

_NONCE_SIZE = 12


def _key_bytes() -> bytes:
    key = get_settings().pii_vault_encryption_key
    if not key:
        raise RuntimeError("PII_VAULT_ENCRYPTION_KEY is not set")
    key_bytes = base64.b64decode(key)
    if len(key_bytes) != 32:
        raise RuntimeError("PII_VAULT_ENCRYPTION_KEY must decode to 32 bytes (AES-256)")
    return key_bytes


def encrypt(plaintext: str) -> bytes:
    aesgcm = AESGCM(_key_bytes())
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt(blob: bytes) -> str:
    aesgcm = AESGCM(_key_bytes())
    nonce, ciphertext = blob[:_NONCE_SIZE], blob[_NONCE_SIZE:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
