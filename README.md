# MedCoreBridge

Sağlık turizmi klinikleri için çok dilli, KVKK/GDPR zırhlı AI ön-triyaj ve lead niteleme köprüsü. Tam ürün/mimari/satış planı için `docs/MedCoreBridge.md`, geliştirme konvansiyonları için `CLAUDE.md`.

## Yapı

- `apps/web` — Next.js widget + klinik paneli
- `apps/api` — FastAPI backend (rıza, PII maskeleme, RAG, LLM orkestrasyon, guardrails)
- `infra` — docker-compose, Supabase migrasyonları

## Geliştirme

```bash
# Backend
cd apps/api
cp .env.example .env   # değerleri doldur
uv run python -m spacy download en_core_web_sm   # PII maskeleme (Presidio) için — pyproject'e
                                                   # eklenemedi (bkz. not), her clone'da elle gerekiyor
uv run uvicorn app.main:app --reload

# Frontend
cd apps/web
pnpm dev

# Redis + API + worker (Docker)
cd infra
docker compose up
```

## Veritabanı migrasyonları

`infra/supabase/migrations/*.sql` — Supabase CLI'nin ürettiği isimlendirme konvansiyonuyla
(`<timestamp>_<açıklama>.sql`) elle yazılır. Uygulamak için:

```bash
cd apps/api && uv run python scripts/migrate.py
```

Uygulanan dosyalar `schema_migrations` tablosunda tutulur, script idempotent'tir.

## Test

```bash
cd apps/api && uv run pytest
cd apps/web && pnpm build
```

## PII Maskeleme

`apps/api/app/services/pii_masking/` — Presidio (analyzer+anonymizer) ile PII tespiti,
tespit edilen değer `[HASTA_A]`, `[TELEFON_1]` gibi bir token'a çevrilir; gerçek değer
AES-256-GCM ile şifrelenip `pii_vault` tablosuna yazılır (conversation başına tutarlı
token — aynı değer aynı token'ı alır). `PII_VAULT_ENCRYPTION_KEY` (32 byte, base64) `.env`'de
olmalı. Türkçe TC Kimlik No (checksum doğrulamalı) ve pasaport için özel recognizer'lar var;
isim (PERSON) tespiti `en_core_web_sm` spaCy modeliyle yapılıyor — küçük/İngilizce model
olduğu için Türkçe isimlerde NER bazen tutarsız kalabilir (bkz. `tests/test_pii_masking.py`
notu); ileride daha güçlü/çok dilli bir model gerekebilir.
