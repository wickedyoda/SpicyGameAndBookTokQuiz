import unittest
from pathlib import Path
from unittest.mock import patch

from spicy_quiz.config import SourceConfig, SourcesFile
from spicy_quiz.models import ScrapedQuestion
from spicy_quiz.service import SpicyQuizService


class _StoreStub:
    def __init__(self) -> None:
        self.questions: list[ScrapedQuestion] = []

    def upsert_questions(self, questions: list[ScrapedQuestion]) -> int:
        self.questions.extend(questions)
        return len(questions)

    def list_questions(self, category: str | None = None) -> list[ScrapedQuestion]:
        return self.questions


class RefreshServiceTests(unittest.TestCase):
    def test_refresh_continues_when_one_source_fails(self) -> None:
        store = _StoreStub()
        service = SpicyQuizService(
            store,
            SourcesFile(
                user_agent="ua",
                sources=(
                    SourceConfig(
                        name="good-source",
                        category="good",
                        source_type="local-json",
                        path="/tmp/good.json",
                    ),
                    SourceConfig(
                        name="bad-source",
                        category="bad",
                        url="https://example.com",
                    ),
                ),
            ),
        )

        with (
            patch("spicy_quiz.service.load_local_json_source") as load_local_json_source,
            patch("spicy_quiz.service.scrape_source") as scrape_source,
        ):
            load_local_json_source.return_value = [
                ScrapedQuestion(
                    prompt="Working prompt",
                    category="good",
                    source_name="good-source",
                    source_url="local://good",
                )
            ]
            scrape_source.side_effect = RuntimeError("blocked")

            result = service.refresh()

        self.assertEqual(result["saved_count"], 1)
        self.assertEqual(result["successful_sources"], ["good-source"])
        self.assertEqual(result["failed_sources"], [{"name": "bad-source", "error": "blocked"}])


if __name__ == "__main__":
    unittest.main()
