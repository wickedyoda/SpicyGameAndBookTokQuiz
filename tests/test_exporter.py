import json
import tempfile
import unittest
from pathlib import Path

from spicy_quiz.exporter import export_questions
from spicy_quiz.models import ScrapedQuestion


class ExporterTests(unittest.TestCase):
    def test_writes_index_and_pack_files(self) -> None:
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
            self.assertEqual(index_payload["pack_count"], 2)
            self.assertEqual(len(index_payload["packs"]), 2)

            dirty_truth_pack = next(pack for pack in index_payload["packs"] if pack["id"] == "dirty-truth")
            dirty_truth_path = manifest_dir / dirty_truth_pack["path"]
            self.assertTrue(dirty_truth_path.exists())

            pack_payload = json.loads(dirty_truth_path.read_text(encoding="utf-8"))
            self.assertEqual(pack_payload["prompt_count"], 1)
            self.assertEqual(pack_payload["prompts"][0]["id"], "dirty-truth_0001")
            self.assertEqual(pack_payload["prompts"][0]["text"], "Question one?")

            booktok_pack = next(pack for pack in index_payload["packs"] if pack["id"] == "booktok")
            booktok_path = manifest_dir / booktok_pack["path"]
            booktok_payload = json.loads(booktok_path.read_text(encoding="utf-8"))
            self.assertEqual(booktok_payload["prompts"][0]["metadata"]["level"], 2)


if __name__ == "__main__":
    unittest.main()
