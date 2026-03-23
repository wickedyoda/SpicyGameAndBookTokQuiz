from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re

from spicy_quiz.models import ScrapedQuestion


SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or "items"


def _manifest_filename(prefix: str, name: str) -> str:
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}.{_slugify(name)}.{digest}.json"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def export_questions(index_path: Path, questions: list[ScrapedQuestion]) -> None:
    manifest_dir = index_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)

    for stale_file in manifest_dir.glob("*.json"):
        stale_file.unlink()

    category_counts = Counter(question.category for question in questions)
    source_counts = Counter(question.source_name for question in questions)
    generated_at = datetime.now(timezone.utc).isoformat()

    all_filename = "questions.all.json"
    _write_json(
        manifest_dir / all_filename,
        {
            "generated_at": generated_at,
            "question_count": len(questions),
            "questions": [question.to_dict() for question in questions],
        },
    )

    categories: dict[str, dict[str, object]] = {}
    for category in sorted(category_counts):
        filename = _manifest_filename("category", category)
        category_questions = [question.to_dict() for question in questions if question.category == category]
        _write_json(
            manifest_dir / filename,
            {
                "generated_at": generated_at,
                "category": category,
                "question_count": len(category_questions),
                "questions": category_questions,
            },
        )
        categories[category] = {
            "path": filename,
            "question_count": len(category_questions),
        }

    sources: dict[str, dict[str, object]] = {}
    for source_name in sorted(source_counts):
        filename = _manifest_filename("source", source_name)
        source_questions = [question.to_dict() for question in questions if question.source_name == source_name]
        _write_json(
            manifest_dir / filename,
            {
                "generated_at": generated_at,
                "source_name": source_name,
                "question_count": len(source_questions),
                "questions": source_questions,
            },
        )
        sources[source_name] = {
            "path": filename,
            "question_count": len(source_questions),
        }

    payload = {
        "generated_at": generated_at,
        "question_count": len(questions),
        "categories": sorted(category_counts),
        "category_counts": dict(sorted(category_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "files": {
            "all_questions": all_filename,
            "categories": categories,
            "sources": sources,
        },
    }

    _write_json(index_path, payload)
