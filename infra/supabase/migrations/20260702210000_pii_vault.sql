-- Faz 1/Hafta 3: PII tokenizasyon vault
-- Gerçek PII değeri AES-256-GCM ile uygulama katmanında şifrelenip encrypted_value'ya yazılır
-- (nonce+ciphertext birlikte). Token, aynı conversation içinde aynı değer için sabit kalır.

create table pii_vault (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations (id) on delete cascade,
  token text not null,
  entity_type text not null,
  encrypted_value bytea not null,
  created_at timestamptz not null default now(),
  unique (conversation_id, token)
);

create index pii_vault_conversation_id_idx on pii_vault (conversation_id);

alter table pii_vault enable row level security;
