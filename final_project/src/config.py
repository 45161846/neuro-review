# src/config.py
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")

    github_access_token: str = Field(env="GITHUB_ACCESS_TOKEN")
    github_webhook_secret: str = Field(env="GITHUB_WEBHOOK_SECRET")

    deepseek_api_key: str = Field(env="DEEPSEEK_API_KEY")
    ai_model: str = Field(default="deepseek-chat", env="AI_MODEL")
    ai_max_tokens: int = Field(default=4000, env="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.2, env="AI_TEMPERATURE")

    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="reviewer", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD")

    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings(
    github_access_token="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",
    github_webhook_secret="3744yQrgp0kmQRESWlbTzyByFVt_2ZcqVx7NSgThtp2gJe2pa",
    deepseek_api_key="sk-87c86384028d48d89dc85e84e88a3edf",
    postgres_password="qwerty"
)