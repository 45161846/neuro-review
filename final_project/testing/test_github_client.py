import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def github_client():
    with patch('final_project.src.github.client.settings') as mock_settings:
        mock_settings.github_access_token = "test_token"
        from final_project.src.github.client import GitHubClient
        client = GitHubClient()
        client.client = AsyncMock()
        return client


@pytest.mark.asyncio
async def test_get_open_pull_requests_success(github_client):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "title": "Test PR"}]
    mock_response.raise_for_status = MagicMock()
    github_client.client.get.return_value = mock_response

    result = await github_client.get_open_pull_requests("owner/repo")

    assert len(result) == 1
    assert result[0]["id"] == 1
    github_client.client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_open_pull_requests_failure(github_client):
    github_client.client.get.side_effect = Exception("Network error")

    result = await github_client.get_open_pull_requests("owner/repo")

    assert result == []


@pytest.mark.asyncio
async def test_get_pull_request(github_client):
    mock_pr_response = MagicMock()
    mock_pr_response.json.return_value = {
        "number": 123,
        "title": "Test PR",
        "user": {"login": "testuser"},
        "base": {"sha": "base123"},
        "head": {"sha": "head123"}
    }
    mock_pr_response.raise_for_status = MagicMock()

    mock_files_response = MagicMock()
    mock_files_response.json.return_value = [{"filename": "test.py", "changes": 10}]

    mock_diff_response = MagicMock()
    mock_diff_response.text = "diff --git a/test.py"

    github_client.client.get.side_effect = [
        mock_pr_response, mock_files_response, mock_diff_response
    ]

    from final_project.src.github.client import PullRequestData
    result = await github_client.get_pull_request("owner/repo", 123)

    assert isinstance(result, PullRequestData)
    assert result.pr_id == 123
    assert result.title == "Test PR"
    assert result.author == "testuser"
    assert result.diff_text == "diff --git a/test.py"


@pytest.mark.asyncio
async def test_get_pr_files(github_client):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"filename": "test.py", "changes": 5}]
    mock_response.raise_for_status = MagicMock()
    github_client.client.get.return_value = mock_response

    result = await github_client.get_pr_files("owner/repo", 123)

    assert len(result) == 1
    assert result[0]["filename"] == "test.py"


@pytest.mark.asyncio
async def test_get_pr_diff(github_client):
    mock_response = MagicMock()
    mock_response.text = "test diff content"
    mock_response.raise_for_status = MagicMock()
    github_client.client.get.return_value = mock_response

    result = await github_client.get_pr_diff("owner/repo", 123)

    assert result == "test diff content"


@pytest.mark.asyncio
async def test_add_comment_to_pr_success(github_client):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    github_client.client.post.return_value = mock_response

    with patch('final_project.src.github.client.logger') as mock_logger:
        result = await github_client.add_comment_to_pr("owner/repo", 123, "Test comment")

        assert result is True
        mock_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_add_comment_to_pr_failure(github_client):
    github_client.client.post.side_effect = Exception("Failed to post")

    with patch('final_project.src.github.client.logger') as mock_logger:
        result = await github_client.add_comment_to_pr("owner/repo", 123, "Test comment")

        assert result is False
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_get_repository_info(github_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "repo", "owner": {"login": "owner"}}
    mock_response.raise_for_status = MagicMock()
    github_client.client.get.return_value = mock_response

    result = await github_client.get_repository_info("owner/repo")

    assert result["name"] == "repo"


@pytest.mark.asyncio
async def test_close(github_client):
    github_client.client.aclose = AsyncMock()

    await github_client.close()

    github_client.client.aclose.assert_called_once()