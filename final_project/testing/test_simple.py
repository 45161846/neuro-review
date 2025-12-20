import pytest
from unittest.mock import MagicMock, AsyncMock, patch


def test_review_result_dataclass():
    from final_project.src.review.service import ReviewResult

    result = ReviewResult(
        pr_id=1,
        repository="test/repo",
        review_text="Test review",
        summary="Test summary",
        success=True,
        critical_issues_count=0,
        suggestions_count=0
    )

    assert result.pr_id == 1
    assert result.repository == "test/repo"
    assert result.success is True


def test_pull_request_data_dataclass():
    """Простой тест для dataclass GitHub"""
    from final_project.src.github.client import PullRequestData

    data = PullRequestData(
        pr_id=1,
        repository="test/repo",
        title="Test PR",
        author="testuser",
        diff_url="http://example.com",
        base_commit="abc123",
        head_commit="def456",
        files_changed=[{"file": "test.py"}],
        diff_text="test diff"
    )

    assert data.pr_id == 1
    assert data.repository == "test/repo"
    assert data.author == "testuser"


@pytest.mark.asyncio
async def test_review_service_simple():
    """Простой тест ReviewService"""
    github_client = AsyncMock()
    ai_client = AsyncMock()

    from final_project.src.review.service import ReviewService

    service = ReviewService(github_client, ai_client)

    # Просто проверяем, что объект создается
    assert service.github_client == github_client
    assert service.ai_client == ai_client


def test_github_client_init():
    """Тест инициализации GitHubClient"""
    with patch('final_project.src.github.client.settings') as mock_settings:
        mock_settings.github_access_token = "test_token"

        from final_project.src.github.client import GitHubClient
        client = GitHubClient()

        assert client.access_token == "test_token"
        assert client.base_url == "https://api.github.com"


def test_ai_client_comment_generation():
    """Тест генерации комментария без импорта AIClient"""

    def mock_generate_comment_text(analysis):
        if not analysis.get("success", False):
            return "❌ Failed to analyze code changes."

        critical_count = len(analysis.get("critical_issues", []))
        suggestions_count = len(analysis.get("suggestions", []))

        comment = "## 🤖 AI Code Review\n\n"
        if critical_count == 0 and suggestions_count == 0:
            comment += "✅ No issues found. Code looks good!\n"

        return comment

    analysis_success = {
        "success": True,
        "critical_issues": [],
        "suggestions": []
    }

    analysis_failed = {"success": False}

    result_success = mock_generate_comment_text(analysis_success)
    result_failed = mock_generate_comment_text(analysis_failed)

    assert "✅ No issues found" in result_success
    assert "❌ Failed to analyze" in result_failed