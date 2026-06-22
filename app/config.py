from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    admin_telegram_id: int | None = None
    database_url: str = "postgresql+asyncpg://aa_bot:change_me@127.0.0.1:5432/aa_bot"
    redis_url: str = "redis://127.0.0.1:6379/0"
    public_mode: bool = False
    invite_code: str = "aa-test"
    openrouter_api_key: str = ""
    llm_api_key: str = ""
    llm_model: str = "openai/gpt-4.1-mini"
    llm_base_url: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
