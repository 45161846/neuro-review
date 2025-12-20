import sys
import os
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    os.environ.update({
        "GITHUB_ACCESS_TOKEN": "test_token",
        "GITHUB_WEBHOOK_SECRET": "test_secret",
        "AI_BASE_URL": "https://api.test.com",
        "AI_API_KEY": "test_ai_key",
        "POSTGRES_PASSWORD": "test_password"
    })

    exit_code = pytest.main([
        "testing/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-fail-under=65"
    ])
    sys.exit(exit_code)