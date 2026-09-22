from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = Field(min_length=10)
    database_url: str
    admin_ids: list[int] = []
    card_number: str = Field(min_length=4)
    card_owner: str = Field(min_length=2, validation_alias="CARD_OWNER")
    support_contact: str = ""
    receipt_max_bytes: int = Field(default=5 * 1024 * 1024, ge=1024, le=20 * 1024 * 1024)
    receipt_mime_types: list[str] = ["image/jpeg", "image/png", "application/pdf"]
    environment: str = "development"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @property
    def card_holder(self) -> str: return self.card_owner

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"): return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"): return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value):
        if isinstance(value, str): return [int(x.strip()) for x in value.split(",") if x.strip()]
        return value

settings = Settings()
