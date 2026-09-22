from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(min_length=10)
    database_url: str
    admin_ids: list[int] = Field(default_factory=list)
    card_number: str = Field(min_length=4)
    card_owner: str = Field(min_length=2, validation_alias="CARD_OWNER")
    support_contact: str = ""
    receipt_max_bytes: int = Field(
        default=5 * 1024 * 1024,
        ge=1024,
        le=20 * 1024 * 1024,
    )
    receipt_mime_types: list[str] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/png",
            "application/pdf",
        ]
    )
    environment: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def card_holder(self) -> str:
        return self.card_owner

    def is_admin(self, telegram_user_id: int | None) -> bool:
        """Authorize administrators by Telegram numeric user ID only."""
        return telegram_user_id is not None and telegram_user_id in self.admin_ids

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value):
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        return value


settings = Settings()
