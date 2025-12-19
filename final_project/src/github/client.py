import logging
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from final_project.src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PullRequestData:
    pr_id: int
    repository: str
    title: str
    author: str
    diff_url: str
    base_commit: str
    head_commit: str
    files_changed: List[Dict[str, Any]]
    diff_text: str = ""


class GitHubClient:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.github_access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0
        )

    async def get_open_pull_requests(self, repository: str, head: str = None) -> List[Dict[str, Any]]:
        endpoint = f"/repos/{repository}/pulls"
        params = {"state": "open"}

        if head:
            params["head"] = head

        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get open PRs for {repository}: {e}")
            return []

    async def get_pull_request(self, repo: str, pr_number: int) -> PullRequestData:
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        response = await self.client.get(url)
        response.raise_for_status()
        pr_data = response.json()

        diff_url = pr_data.get("diff_url", "")
        base_commit = pr_data.get("base", {}).get("sha", "")
        head_commit = pr_data.get("head", {}).get("sha", "")

        files_changed = await self.get_pr_files(repo, pr_number)
        diff_text = await self.get_pr_diff(repo, pr_number)

        return PullRequestData(
            pr_id=pr_number,
            repository=repo,
            title=pr_data.get("title", ""),
            author=pr_data.get("user", {}).get("login", ""),
            diff_url=diff_url,
            base_commit=base_commit,
            head_commit=head_commit,
            files_changed=files_changed,
            diff_text=diff_text
        )

    async def get_pr_files(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "Authorization": f"token {self.access_token}",
        }
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    async def add_comment_to_pr(self, repo: str, pr_number: int, comment: str) -> bool:
        url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
        payload = {"body": comment}

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully added comment to PR #{pr_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment to PR #{pr_number}: {e}")
            return False

    async def get_repository_info(self, repo: str) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{repo}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()