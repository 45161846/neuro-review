import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def review_service():
    github_client = AsyncMock()
    ai_client = AsyncMock()
    from final_project.src.review.service import ReviewService
    return ReviewService(github_client, ai_client)


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.mark.asyncio
async def test_review_pull_request_success(review_service, mock_db_session):
    mock_pr_data = MagicMock()
    mock_pr_data.diff_text = "test diff"
    mock_pr_data.title = "Test PR"
    mock_pr_data.files_changed = [{"filename": "test.py"}]

    review_service.github_client.get_pull_request.return_value = mock_pr_data

    ai_analysis = {
        "success": True,
        "summary": "Good code",
        "critical_issues": [{"file": "test.py", "line": 1, "issue": "bug"}],
        "suggestions": [{"file": "test.py", "line": 2, "suggestion": "improve"}],
        "overall_quality_score": 85
    }
    review_service.ai_client.analyze_code_diff.return_value = ai_analysis
    review_service.ai_client.generate_comment_text.return_value = "AI Review Comment"
    review_service.github_client.add_comment_to_pr.return_value = True

    result = await review_service.review_pull_request(
        repository="owner/repo",
        pr_number=123,
        db_session=mock_db_session
    )

    from final_project.src.review.service import ReviewResult
    assert isinstance(result, ReviewResult)
    assert result.pr_id == 123
    assert result.repository == "owner/repo"
    assert result.summary == "Good code"
    assert result.success is True
    assert result.critical_issues_count == 1
    assert result.suggestions_count == 1
    review_service.github_client.add_comment_to_pr.assert_called_once()


@pytest.mark.asyncio
async def test_review_pull_request_ai_failure(review_service, mock_db_session):
    mock_pr_data = MagicMock()
    mock_pr_data.diff_text = "test diff"
    mock_pr_data.title = "Test PR"
    mock_pr_data.files_changed = []

    review_service.github_client.get_pull_request.return_value = mock_pr_data

    ai_analysis = {"success": False}
    review_service.ai_client.analyze_code_diff.return_value = ai_analysis

    result = await review_service.review_pull_request(
        repository="owner/repo",
        pr_number=123,
        db_session=mock_db_session
    )

    assert result.success is False
    assert result.summary == "AI analysis failed"
    assert result.critical_issues_count == 0
    review_service.github_client.add_comment_to_pr.assert_not_called()


@pytest.mark.asyncio
async def test_review_pull_request_comment_failure(review_service, mock_db_session):
    mock_pr_data = MagicMock()
    mock_pr_data.diff_text = "test diff"
    mock_pr_data.title = "Test PR"
    mock_pr_data.files_changed = []

    review_service.github_client.get_pull_request.return_value = mock_pr_data

    ai_analysis = {"success": True, "summary": "Test", "critical_issues": [], "suggestions": []}
    review_service.ai_client.analyze_code_diff.return_value = ai_analysis
    review_service.ai_client.generate_comment_text.return_value = "Comment"
    review_service.github_client.add_comment_to_pr.return_value = False

    result = await review_service.review_pull_request(
        repository="owner/repo",
        pr_number=123,
        db_session=mock_db_session
    )

    assert result.success is False
    assert result.critical_issues_count == 0


@pytest.mark.asyncio
async def test_review_pull_request_exception(review_service, mock_db_session):
    review_service.github_client.get_pull_request.side_effect = Exception("Test error")

    with patch('final_project.src.review.service.logger') as mock_logger:
        result = await review_service.review_pull_request(
            repository="owner/repo",
            pr_number=123,
            db_session=mock_db_session
        )

        assert result.success is False
        assert "Error: Test error" in result.summary
        mock_logger.error.assert_called_once()