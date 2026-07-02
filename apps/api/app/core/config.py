from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""
    pii_vault_encryption_key: str = ""

    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""

    whatsapp_cloud_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_webhook_verify_token: str = ""

    sentry_dsn: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
