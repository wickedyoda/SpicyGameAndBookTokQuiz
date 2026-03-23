import unittest

from spicy_quiz.text import extract_question_candidates, normalize_question_text


class NormalizeQuestionTextTests(unittest.TestCase):
    def test_removes_numbered_prefix(self) -> None:
        self.assertEqual(
            normalize_question_text("12. What trope would ruin the mood?"),
            "What trope would ruin the mood?",
        )

    def test_removes_custom_prefix(self) -> None:
        self.assertEqual(
            normalize_question_text("Question: Which character is the red flag?", ("Question:",)),
            "Which character is the red flag?",
        )

    def test_splits_multiple_numbered_questions(self) -> None:
        self.assertEqual(
            extract_question_candidates(
                "10. Which is your go-to place to have s#x? 11. What is your preference between men taking the lead vs. women taking the lead?",
                numbered_only=True,
            ),
            [
                "Which is your go-to place to have s#x?",
                "What is your preference between men taking the lead vs. women taking the lead?",
            ],
        )

    def test_numbered_only_skips_non_numbered_text(self) -> None:
        self.assertEqual(
            extract_question_candidates(
                "This is intro copy, not a question block.",
                numbered_only=True,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
