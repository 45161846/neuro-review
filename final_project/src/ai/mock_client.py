import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MockAIClient:
    """Mock AI client for testing without OpenAI API"""

    def __init__(self):
        self.mock_mode = True
        logger.info("Using MockAIClient - no API calls will be made")

    async def analyze_code_diff(
            self,
            diff_text: str,
            pr_title: str,
            repo_name: str,
            files_changed: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock analysis that returns fake data"""
        logger.info(f"Mock analysis for PR: {pr_title}, files: {len(files_changed)}")

        # Пример мокового анализа
        return {
            "success": True,
            "summary": f"Моковый анализ PR '{pr_title}' в репозитории {repo_name}. "
                       f"Изменено файлов: {len(files_changed)}. "
                       f"Размер diff: {len(diff_text)} символов.",
            "critical_issues": [
                {
                    "file": "src/main.py",
                    "line": 10,
                    "issue": "Небезопасное использование eval()",
                    "suggestion": "Заменить eval() на ast.literal_eval() или json.loads()"
                },
                {
                    "file": "config/database.py",
                    "line": 25,
                    "issue": "Пароль в коде",
                    "suggestion": "Использовать переменные окружения для чувствительных данных"
                }
            ],
            "suggestions": [
                {
                    "file": "utils/helpers.py",
                    "line": 42,
                    "suggestion": "Добавить обработку исключений для сетевых запросов"
                },
                {
                    "file": "tests/test_service.py",
                    "line": 15,
                    "suggestion": "Увеличить покрытие тестами для edge cases"
                }
            ],
            "overall_quality_score": 78,
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }

    async def generate_comment_text(self, analysis: Dict[str, Any]) -> str:
        """Generate PR comment from analysis"""
        if not analysis.get("success", False):
            return "❌ Ошибка анализа кода"

        critical_count = len(analysis.get("critical_issues", []))
        suggestions_count = len(analysis.get("suggestions", []))
        score = analysis.get("overall_quality_score", 0)

        comment = "## 🤖 Автоматический ревью от AI Code Reviewer\n\n"
        comment += f"**Резюме:** {analysis.get('summary', '')}\n\n"
        comment += f"**Оценка качества:** {score}/100\n\n"

        if critical_count > 0:
            comment += f"### ⚠️ Критические проблемы ({critical_count})\n"
            for issue in analysis.get("critical_issues", [])[:5]:
                comment += f"- **{issue.get('file')}:{issue.get('line')}** - {issue.get('issue')}\n"
                if issue.get('suggestion'):
                    comment += f"  *Предложение:* {issue.get('suggestion')}\n"
            comment += "\n"

        if suggestions_count > 0:
            comment += f"### 💡 Предложения по улучшению ({suggestions_count})\n"
            for suggestion in analysis.get("suggestions", [])[:5]:
                comment += f"- **{suggestion.get('file')}:{suggestion.get('line')}** - {suggestion.get('suggestion')}\n"
            comment += "\n"

        if critical_count == 0 and suggestions_count == 0:
            comment += "✅ Код выглядит отлично! Никаких проблем не обнаружено.\n"

        comment += "---\n"
        comment += "*Это автоматический ревью, сгенерированный AI. Проверьте критичные проблемы вручную.*\n"

        if analysis.get("mock"):
            comment += "\n**ℹ️ Это тестовый моковый ревью (без использования AI API)**"

        return comment