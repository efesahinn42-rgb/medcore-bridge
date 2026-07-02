-- MedCoreBridge — Faz 1/Hafta 2: temel şema + rıza loglama + pgvector
-- clinics: multi-tenant kök tablo (dokümanda açıkça listelenmedi ama users/conversations/
--   embeddings hepsi klinik bazında izole olmalı, bu tablo olmadan tenant izolasyonu kurulamaz)

create extension if not exists vector;

create table clinics (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  default_language text not null default 'tr',
  supported_languages text[] not null default array['tr'],
  timezone text not null default 'Europe/Istanbul',
  whatsapp_phone_number_id text,
  crm_integration jsonb not null default '{}'::jsonb,
  status text not null default 'trial' check (status in ('trial', 'active', 'suspended')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- users: hasta/lead (klinik personeli değil — WhatsApp/widget üzerinden yazan kişi)
create table users (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics (id) on delete cascade,
  channel text not null check (channel in ('whatsapp', 'web_widget')),
  whatsapp_wa_id text,
  full_name text,
  phone_number text,
  preferred_language text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (clinic_id, whatsapp_wa_id)
);

create index users_clinic_id_idx on users (clinic_id);

-- consent_logs: rıza olmadan konuşma başlamaz (bkz. MedCoreBridge.md §1, katman 1)
create table consent_logs (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics (id) on delete cascade,
  user_id uuid not null references users (id) on delete cascade,
  consent_type text not null default 'kvkk_gdpr_general',
  consent_given boolean not null,
  consent_text_version text not null,
  language text not null,
  ip_address inet,
  user_agent text,
  created_at timestamptz not null default now()
);

create index consent_logs_user_id_idx on consent_logs (user_id);

create table conversations (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics (id) on delete cascade,
  user_id uuid not null references users (id) on delete cascade,
  channel text not null check (channel in ('whatsapp', 'web_widget')),
  status text not null default 'active' check (status in ('active', 'closed', 'escalated_hitl')),
  language text,
  summary text,
  lead_confidence_score numeric,
  crm_push_status text not null default 'pending'
    check (crm_push_status in ('pending', 'queued', 'success', 'failed', 'dlq')),
  crm_pushed_at timestamptz,
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index conversations_clinic_id_idx on conversations (clinic_id);
create index conversations_user_id_idx on conversations (user_id);

create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations (id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system', 'human_agent')),
  content text not null,
  image_url text,
  vision_result jsonb,
  llm_provider text,
  created_at timestamptz not null default now()
);

create index messages_conversation_id_idx on messages (conversation_id);

-- embeddings: klinik başına RAG bilgi tabanı (text-embedding-3-small = 1536 boyut)
create table embeddings (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics (id) on delete cascade,
  source_document text not null,
  content text not null,
  embedding vector (1536) not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index embeddings_clinic_id_idx on embeddings (clinic_id);
create index embeddings_embedding_hnsw_idx on embeddings using hnsw (embedding vector_cosine_ops);

create function set_updated_at ()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger clinics_set_updated_at before update on clinics
  for each row execute function set_updated_at ();
create trigger users_set_updated_at before update on users
  for each row execute function set_updated_at ();
create trigger conversations_set_updated_at before update on conversations
  for each row execute function set_updated_at ();

-- RLS: backend sadece service_role ile bağlanıyor (RLS'i bypass eder); anon/authenticated
-- için hiç politika tanımlamıyoruz (default-deny) — frontend Supabase'e doğrudan konuşmuyor.
alter table clinics enable row level security;
alter table users enable row level security;
alter table consent_logs enable row level security;
alter table conversations enable row level security;
alter table messages enable row level security;
alter table embeddings enable row level security;
