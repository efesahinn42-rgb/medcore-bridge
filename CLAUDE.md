# MedCoreBridge — Çok Dilli Sağlık Turizmi AI Köprüsü

> Kapsamlı mimari/ürün/satış planı: `MedCoreBridge.md` (bu dosya sadece teknik çalışma rehberi).
> Ürün bir CRM DEĞİLDİR — dış kanallar (WhatsApp/web) ile kliniğin CRM'i arasında çalışan
> rıza-zırhlı, RAG tabanlı bilgilendirme + ön triyaj asistanıdır. Teşhis/tedavi önermez.

## Stack

### Frontend (widget + klinik paneli)
- Next.js (App Router) + TypeScript
- Tailwind CSS + shadcn/ui (çok dilli, Arapça RTL desteği şart)
- Barındırma: Vercel

### Backend (asıl iş mantığı burada)
- **Python + FastAPI** — rıza, PII maskeleme, RAG, LLM orkestrasyon, guardrails
- **Celery + Redis** — arka plan işleri (görsel işleme, CRM gönderimi, retry kuyruğu)
- Docker (her ortamda aynı paket)
- Barındırma: MVP → Render/Railway/Fly.io · Üretim → AWS ECS Fargate

### Yapay zekâ
- Ana LLM: **Anthropic Claude API** (Pro aboneliği DEĞİL — ayrı API hesabı, zero-retention/no-training DPA gerekir)
- Failover: OpenAI + Google Gemini API (429/500'de devreye girer)
- Görsel: Gemini Vision (saç/diş foto ön sınıflandırma, teşhis değil)
- RAG: pgvector + embedding modeli (klinik bilgisi dışına çıkmaz)
- Semantik cache: Redis
- Guardrails: Guardrails AI + özel kurallar (jailbreak/injection giriş, tıbbi iddia/PII sızıntı çıkış)
- Opsiyonel self-hosted: Llama 3.1/Mistral + vLLM (veri yurt dışına çıkmasın isteyen kurumlar için)

### Veri / güvenlik / gözlem
- Supabase (PostgreSQL + pgvector) — kullanıcı, konuşma, rıza, lead, RAG deposu
- Tokenizasyon vault (KMS/AES-256) — PII gerçek veri LLM'e gitmez
- AWS Secrets Manager / SSM — API anahtarları
- AWS WAF + CloudFront (üretim)
- Langfuse (self-hosted) — LLM maliyet/gecikme/kalite izleme
- Sentry — hata/performans
- Langfuse Evals / promptfoo / Ragas — kalite + groundedness ölçümü

### Mesajlaşma
- Meta WhatsApp Cloud API (Twilio değil — doğrudan)

## Klasör Yapısı (öneri — henüz oluşturulmadı)
```
apps/
  web/                  → Next.js widget + klinik paneli
    app/
    components/
      ui/
      features/
  api/                  → FastAPI backend
    app/
      routers/          → API endpoint'leri
      services/         → rıza, maskeleme, RAG, guardrails, LLM orkestrasyon
      tasks/             → Celery görevleri (CRM push, görsel işleme, retry)
      models/            → Pydantic/DB modelleri
    tests/
    Dockerfile
```

## Konvansiyonlar
- Backend'de tüm iş mantığı FastAPI'de; Next.js sadece UI + Vercel'e ince bir API proxy katmanı (gerekirse)
- Hasta mesajı LLM'e gitmeden ÖNCE PII maskeleme middleware'inden geçer (bkz. MedCoreBridge.md §3.4, Faz1/Hafta3)
- RAG dışına çıkan/kaynaksız yanıt YASAK — guardrail seviyesinde engellenir
- Her CRM/dış sistem yazımı senkron değil, Celery kuyruğu üzerinden (sıfır veri kaybı ilkesi — bkz. §6)
- Entegrasyon tek yönlü: kliniğin sistemine yazarız, veri çekmeyiz

## Komutlar (proje iskeleti kurulunca netleşecek)
- backend dev: `uvicorn app.main:app --reload`
- backend test: `pytest`
- worker: `celery -A app.tasks worker --loglevel=info`
- frontend dev: `pnpm dev` (apps/web içinde)
- db: Supabase CLI / dashboard üzerinden migrasyon

## Model Stratejisi
- Küçük düzeltme → `/model haiku`
- Normal geliştirme → sonnet (default)
- Mimari karar / guardrail tasarımı / hukuki-teknik ayrım → `/model opusplan`
- Yüksek doğruluk gereken (PII maskeleme, rıza akışı, guardrails) → `/effort xhigh`

## Aktif Skills (proje bazlı öncelik)
- `/security-review` — her PII/rıza/guardrail değişikliğinden önce ZORUNLU
- `/tdd` / `/test-driven-development` — özellikle maskeleme, rıza loglama, failover mantığı
- `/diagnosing-bugs`, `/systematic-debugging` — RAG/LLM davranış hataları
- `/ponytail full` — gereksiz soyutlama/bağımlılık önleme (özellikle backend serviste)
- `/grill-me` — Faz 0/1 kapsam netleştirme
- `/verification-before-completion` — özellikle guardrail/failover claim'lerinde
- `/handoff` — oturum devri
- `codebase-memory` skill/MCP — backend büyüdükçe call chain/RAG akışını izlemek için

## MCP Kullanım Rehberi
- `context7` → FastAPI/Celery/Supabase/Next.js güncel doküman: "use context7"
- `filesystem` → proje dosyalarına hızlı erişim
- `playwright` → widget UI testi, WhatsApp akış demo kaydı
- `github` → PR/issue yönetimi (token gerekli — bkz. settings.json)
- `vercel` → frontend deploy/env yönetimi
- `headroom` → uzun planlama oturumlarında token sıkıştırma
- `codebase-memory-mcp` → backend koddan kod grafiği: `index_repository`
- `supabase` (eklenecek) → şema/migrasyon/RLS yönetimi — bkz. settings.json notu
- Sentry / WhatsApp MCP → Faz 2-4'te canlıya yaklaşırken eklenmesi önerilir, MVP'de zorunlu değil

## Güvenlik Kontrol Listesi (bkz. MedCoreBridge.md §13 — tam liste orada)
- [ ] .env / secrets .gitignore'da, kodda hardcode YOK
- [ ] Tüm dış girdi (WhatsApp mesajı, dosya) sistem sınırında doğrulanıyor
- [ ] PII maskeleme (NER) LLM çağrısından önce zorunlu ara katman
- [ ] Rıza (KVKK/GDPR) olmadan konuşma başlamıyor; IP+zaman damgası loglanıyor
- [ ] Guardrails: giriş (injection/jailbreak) + çıkış (tıbbi iddia/PII sızıntısı)
- [ ] LLM sağlayıcı zero-retention/no-training DPA (Pro aboneliği DEĞİL, API hesabı)
- [ ] Secrets AWS Secrets Manager/SSM'de, environment variable'da, kodda değil
- [ ] SQL/DB erişimi parameterized (Supabase client / SQLAlchemy)
