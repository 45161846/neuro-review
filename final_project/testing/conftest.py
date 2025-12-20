import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import os

os.environ.update({
    "GITHUB_ACCESS_TOKEN": "test_token",
    "GITHUB_WEBHOOK_SECRET": "test_secret",
    "AI_BASE_URL": "https://api.test.com",
    "AI_API_KEY": "test_ai_key",
    "POSTGRES_PASSWORD": "test_password"
})


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    session = AsyncMock()

    mock_execute = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar = MagicMock(return_value=1)
    mock_execute.return_value = mock_result

    session.execute = mock_execute
    return session