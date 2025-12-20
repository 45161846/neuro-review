import pytest
from unittest.mock import patch


def test_settings_defaults():
    with patch.dict('os.environ', {
        "GITHUB_ACCESS_TOKEN": "test_token",
        "GITHUB_WEBHOOK_SECRET": "test_secret",
        "AI_BASE_URL": "https://api.test.com",
        "AI_API_KEY": "test_ai_key",
        "POSTGRES_PASSWORD": "test_password"
    }, clear=True):
        from final_project.src.config import Settings
        settings = Settings()

        assert settings.app_env == "development"
        assert settings.debug is True
        assert settings.ai_model == "deepseek-chat"


def test_database_url_property():
    with patch.dict('os.environ', {
        "GITHUB_ACCESS_TOKEN": "test_token",
        "GITHUB_WEBHOOK_SECRET": "test_secret",
        "AI_BASE_URL": "https://api.test.com",
        "AI_API_KEY": "test_ai_key",
        "POSTGRES_PASSWORD": "test_password"
    }, clear=True):
        from final_project.src.config import Settings
        settings = Settings()

        assert hasattr(settings, 'database_url')
        assert 'postgresql+asyncpg' in settings.database_url