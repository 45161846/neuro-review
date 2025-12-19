import logging
from dataclasses import dataclass
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    pr_id: int
    repository: str
    review_text: str
    summary: str
    success: bool
    critical_issues_count: int
    suggestions_count: int


class ReviewService:
    def __init__(self, github_client, ai_client):
        self.github_client = github_client
        self.ai_client = ai_client

    async def review_pull_request(
            self,
            repository: str,
            pr_number: int,
            db_session: AsyncSession
    ) -> ReviewResult:
        try:
            logger.info(f"Starting review for PR #{pr_number} in {repository}")

            pr_data = await self.github_client.get_pull_request(repository, pr_number)

            ai_analysis = await self.ai_client.analyze_code_diff(
                diff_text=pr_data.diff_text,
                pr_title=pr_data.title,
                repo_name=repository,
                files_changed=pr_data.files_changed
            )

            if not ai_analysis.get("success", False):
                logger.error(f"AI analysis failed for PR #{pr_number}")
                return ReviewResult(
                    pr_id=pr_number,
                    repository=repository,
                    review_text="",
                    summary="AI analysis failed",
                    success=False,
                    critical_issues_count=0,
                    suggestions_count=0
                )

            comment_text = await self.ai_client.generate_comment_text(ai_analysis)

            comment_success = await self.github_client.add_comment_to_pr(
                repository, pr_number, comment_text
            )

            if comment_success:
                logger.info(f"Comment posted successfully to PR #{pr_number}")
            else:
                logger.error(f"Failed to post comment to PR #{pr_number}")

            critical_count = len(ai_analysis.get("critical_issues", []))
            suggestions_count = len(ai_analysis.get("suggestions", []))

            return ReviewResult(
                pr_id=pr_number,
                repository=repository,
                review_text=comment_text,
                summary=ai_analysis.get("summary", ""),
                success=comment_success,
                critical_issues_count=critical_count,
                suggestions_count=suggestions_count
            )

        except Exception as e:
            logger.error(f"Error reviewing PR #{pr_number}: {e}")
            return ReviewResult(
                pr_id=pr_number,
                repository=repository,
                review_text="",
                summary=f"Error: {e}",
                success=False,
                critical_issues_count=0,
                suggestions_count=0
            )
