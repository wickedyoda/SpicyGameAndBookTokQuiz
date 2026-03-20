from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from spicy_quiz.models import ScrapedQuestion


def export_questions(path: Path, questions: list[ScrapedQuestion]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    category_counts = Counter(question.category for question in questions)
    source_counts = Counter(question.source_name for question in questions)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "question_count": len(questions),
        "categories": sorted(category_counts),
        "category_counts": dict(sorted(category_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "questions": [question.to_dict() for question in questions],
    }

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
