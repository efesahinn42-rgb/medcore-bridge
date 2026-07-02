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
