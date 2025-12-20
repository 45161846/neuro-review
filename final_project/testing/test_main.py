from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


def test_root():
    from final_project.src.main import app
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI Code Reviewer Bot for GitHub"
    assert data["status"] == "running"


@patch('final_project.src.main.get_db')
def test_health_check_success(mock_get_db):
    from final_project.src.main import app
    client = TestClient(app)

    # Мокаем асинхронный генератор
    mock_db_session = AsyncMock()
    mock_execute = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_execute.return_value = mock_result
    mock_db_session.execute = mock_execute

    async def mock_db_generator():
        yield mock_db_session

    mock_get_db.return_value = mock_db_generator()

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch('final_project.src.main.settings')
def test_get_config_debug(mock_settings):
    from final_project.src.main import app
    client = TestClient(app)

    mock_settings.debug = True

    response = client.get("/config")

    assert response.status_code == 200


@patch('final_project.src.main.settings')
def test_get_config_production(mock_settings):
    from final_project.src.main import app
    client = TestClient(app)

    mock_settings.debug = False

    response = client.get("/config")

    assert response.status_code == 403