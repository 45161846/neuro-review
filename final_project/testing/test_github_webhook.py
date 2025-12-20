import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import asyncio


@pytest.fixture
def client():
    mock_settings = MagicMock()
    mock_settings.github_webhook_secret = "test_secret"

    with patch('final_project.src.github.webhook.settings', mock_settings):
        with patch('final_project.src.github.webhook.verify_github_signature', return_value=True):
            from final_project.src.main import app
            return TestClient(app)


@patch('final_project.src.github.webhook.get_ai_client')
@patch('final_project.src.github.webhook.GitHubClient')
@patch('final_project.src.github.webhook.get_db')
@patch('final_project.src.github.webhook.ReviewService')
def test_process_pull_request_async_success(
        mock_review_service, mock_get_db, mock_github_client, mock_get_ai_client
):
    mock_settings = MagicMock()
    mock_settings.github_webhook_secret = "test_secret"

    with patch('final_project.src.github.webhook.settings', mock_settings):
        from final_project.src.github.webhook import process_pull_request_async

        mock_service_instance = AsyncMock()
        mock_review_service.return_value = mock_service_instance

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.critical_issues_count = 2
        mock_result.suggestions_count = 3
        mock_service_instance.review_pull_request.return_value = mock_result

        async def mock_db_generator():
            mock_db_session = AsyncMock()
            yield mock_db_session

        mock_get_db.return_value = mock_db_generator()

        asyncio.run(process_pull_request_async(
            repository_full_name="owner/repo",
            pr_number=123,
            action="opened",
            pr_data={"title": "Test PR"}
        ))

        mock_service_instance.review_pull_request.assert_called_once()


@patch('final_project.src.github.webhook.verify_github_signature', return_value=True)
def test_handle_github_webhook_ping(mock_verify):
    # Создаем клиент с замоканными настройками
    mock_settings = MagicMock()
    mock_settings.github_webhook_secret = "test_secret"

    with patch('final_project.src.github.webhook.settings', mock_settings):
        from final_project.src.main import app
        client = TestClient(app)

        response = client.post(
            "/webhooks/github",
            headers={
                "X-Hub-Signature-256": "sha256=test",
                "X-GitHub-Event": "ping",
                "X-GitHub-Delivery": "test_delivery"
            },
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["event"] == "ping"


@patch('final_project.src.github.webhook.verify_github_signature', return_value=True)
@patch('final_project.src.github.webhook.process_pull_request_async')
def test_handle_github_webhook_pr_opened(mock_process_async, mock_verify):
    mock_settings = MagicMock()
    mock_settings.github_webhook_secret = "test_secret"

    with patch('final_project.src.github.webhook.settings', mock_settings):
        from final_project.src.main import app
        client = TestClient(app)

        payload = {
            "action": "opened",
            "pull_request": {
                "number": 123,
                "title": "Test PR"
            },
            "repository": {
                "full_name": "owner/repo"
            }
        }

        response = client.post(
            "/webhooks/github",
            headers={
                "X-Hub-Signature-256": "sha256=test",
                "X-GitHub-Event": "pull_request",
                "X-GitHub-Delivery": "test_delivery"
            },
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["pr_id"] == 123


def test_test_webhook():
    from final_project.src.main import app
    client = TestClient(app)

    response = client.get("/webhooks/github/test")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["endpoint"] == "/webhooks/github"