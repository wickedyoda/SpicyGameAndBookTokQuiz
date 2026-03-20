import json
import tempfile
import unittest
from pathlib import Path

from spicy_quiz.config import SourceConfig
from spicy_quiz.local_source import load_local_json_source


class LocalSourceTests(unittest.TestCase):
    def test_loads_prompts_and_preserves_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "questions.json"
            source_path.write_text(
                json.dumps(
                    [
                        {
                            "question": "Watch porn together",
                            "level": 2,
                            "tags": [],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            questions = load_local_json_source(
                SourceConfig(
                    name="local-test",
                    source_type="local-json",
                    path=str(source_path),
                    category="partner-desires",
                    prompt_field="question",
                    min_length=5,
                )
            )

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].prompt, "Watch porn together")
        self.assertEqual(questions[0].metadata["level"], 2)


if __name__ == "__main__":
    unittest.main()
