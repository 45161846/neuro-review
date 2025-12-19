import hmac
import hashlib
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from final_project.src.config import settings
from final_project.src.database import get_db
from final_project.src.github.client import GitHubClient
from final_project.src.ai.client import AIClient
from final_project.src.review.service import ReviewService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ai_client():
    """Get AI client - use mock if no API key"""
    if settings.deepseek_api_key:
        from final_project.src.ai.client import AIClient
        return AIClient()
    else:
        from final_project.src.ai.mock_client import MockAIClient
        return MockAIClient()


def verify_github_signature(payload_body: bytes, signature: str) -> bool:
    if not settings.github_webhook_secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True

    secret = settings.github_webhook_secret.encode()
    expected_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()

    expected_header = f"sha256={expected_signature}"
    return hmac.compare_digest(expected_header, signature)


async def process_pull_request_async(
        repository_full_name: str,
        pr_number: int,
        action: str,
        pr_data: Dict[str, Any]
) -> None:
    try:
        github_client = GitHubClient()
        ai_client = get_ai_client()

        async for db_session in get_db():
            service = ReviewService(github_client, ai_client)

            result = await service.review_pull_request(
                repository=repository_full_name,
                pr_number=pr_number,
                db_session=db_session
            )

            logger.info(
                f"PR #{pr_number} processed. "
                f"Critical issues: {result.critical_issues_count}, "
                f"Suggestions: {result.suggestions_count}, "
                f"Success: {result.success}"
            )

    except Exception as e:
        logger.error(f"Failed to process PR #{pr_number}: {e}")


async def process_push_event_async(
        repository_full_name: str,
        ref: str,
        commits: List[Dict[str, Any]],
        before: str,
        after: str
) -> None:
    try:
        branch = ref.replace("refs/heads/", "")
        logger.info(f"Processing push event for branch: {branch}")

        github_client = GitHubClient()
        pull_requests = await github_client.get_open_pull_requests(
            repository_full_name,
            head=branch
        )

        if not pull_requests:
            logger.info(f"No open PRs found for branch: {branch}")
            return

        ai_client = get_ai_client()

        for pr in pull_requests:
            pr_number = pr.get("number")
            if not pr_number:
                continue

            try:
                async for db_session in get_db():
                    service = ReviewService(github_client, ai_client)
                    result = await service.review_pull_request(
                        repository=repository_full_name,
                        pr_number=pr_number,
                        db_session=db_session
                    )

                    logger.info(
                        f"PR #{pr_number} processed after push. "
                        f"Critical issues: {result.critical_issues_count}, "
                        f"Suggestions: {result.suggestions_count}"
                    )
            except Exception as e:
                logger.error(f"Failed to process PR #{pr_number} after push: {e}")

    except Exception as e:
        logger.error(f"Failed to process push event for {repository_full_name}: {e}")


@router.post("/github")
async def handle_github_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    signature = request.headers.get("X-Hub-Signature-256")
    payload_body = await request.body()

    if signature and not verify_github_signature(payload_body, signature):
        logger.warning(f"Invalid signature: {signature}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "ping")
    delivery_id = request.headers.get("X-GitHub-Delivery", "unknown")

    payload = await request.json()

    logger.info(
        f"GitHub webhook received: event={event_type}, "
        f"delivery={delivery_id}"
    )

    if event_type == "ping":
        logger.info("GitHub webhook ping received and verified")
        return {
            "status": "ok",
            "message": "Webhook is active",
            "event": "ping"
        }

    if event_type == "pull_request":
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        repository = payload.get("repository", {}).get("full_name", "")
        pr_number = pr_data.get("number")

        if action in ["opened", "reopened", "synchronize"]:
            logger.info(
                f"Processing PR #{pr_number} - {pr_data.get('title')} "
                f"(action: {action})"
            )

            background_tasks.add_task(
                process_pull_request_async,
                repository,
                pr_number,
                action,
                pr_data
            )

            return {
                "status": "processing",
                "pr_id": pr_number,
                "repository": repository,
                "action": action
            }
        else:
            return {
                "status": "ignored",
                "reason": f"Action '{action}' not processed"
            }

    if event_type == "push":
        ref = payload.get("ref", "")
        commits = payload.get("commits", [])
        repository = payload.get("repository", {}).get("full_name", "")
        before = payload.get("before", "")
        after = payload.get("after", "")

        branch = ref.replace("refs/heads/", "")

        logger.info(
            f"Processing push event for {repository}, branch: {branch}, "
            f"commits: {len(commits)}"
        )

        if not commits:
            logger.info("Push event with no commits, skipping")
            return {
                "status": "ignored",
                "reason": "No commits in push"
            }

        background_tasks.add_task(
            process_push_event_async,
            repository,
            ref,
            commits,
            before,
            after
        )

        return {
            "status": "processing",
            "repository": repository,
            "branch": branch,
            "commits_count": len(commits)
        }

    return {
        "status": "ignored",
        "event": event_type,
        "reason": "Event type not supported"
    }


@router.get("/github/test")
async def test_webhook() -> Dict[str, Any]:
    return {
        "status": "active",
        "endpoint": "/webhooks/github",
        "description": "GitHub webhook handler for AI Code Reviewer"
    }
