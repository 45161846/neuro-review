from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    github_access_token: str
    github_webhook_secret: str

    ai_base_url: str
    ai_api_key: str
    ai_model: str = Field(default="deepseek-chat")
    ai_max_tokens: int = Field(default=4000)
    ai_temperature: float = Field(default=0.2)

    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="reviewer")
    postgres_user: str = Field(default="postgres")
    postgres_password: str

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()