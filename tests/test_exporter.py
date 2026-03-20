import json
import tempfile
import unittest
from pathlib import Path

from spicy_quiz.exporter import export_questions
from spicy_quiz.models import ScrapedQuestion


class ExporterTests(unittest.TestCase):
    def test_writes_index_and_sibling_manifest_files(self) -> None:
        questions = [
            ScrapedQuestion(
                prompt="Question one?",
                category="dirty-truth",
                source_name="source-a",
                source_url="https://example.com/a",
            ),
            ScrapedQuestion(
                prompt="Question two?",
                category="booktok",
                source_name="source-b",
                source_url="https://example.com/b",
                metadata={"level": 2},
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "manifests" / "index.json"
            export_questions(index_path, questions)

            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
            manifest_dir = index_path.parent

            self.assertEqual(index_payload["question_count"], 2)
            self.assertEqual(index_payload["files"]["all_questions"], "questions.all.json")

            all_questions_path = manifest_dir / index_payload["files"]["all_questions"]
            self.assertTrue(all_questions_path.exists())

            dirty_truth_path = manifest_dir / index_payload["files"]["categories"]["dirty-truth"]["path"]
            source_a_path = manifest_dir / index_payload["files"]["sources"]["source-a"]["path"]

            self.assertTrue(dirty_truth_path.exists())
            self.assertTrue(source_a_path.exists())

            all_payload = json.loads(all_questions_path.read_text(encoding="utf-8"))
            self.assertEqual(all_payload["question_count"], 2)
            self.assertEqual(all_payload["questions"][1]["metadata"]["level"], 2)


if __name__ == "__main__":
    unittest.main()
