from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spicy_quiz.config import SourceConfig
from spicy_quiz.models import ScrapedQuestion


def load_local_json_source(source: SourceConfig) -> list[ScrapedQuestion]:
    if not source.path:
        raise ValueError(f"Local source '{source.name}' is missing a path.")

    source_path = Path(source.path)
    if not source_path.exists():
        raise FileNotFoundError(f"Local source file not found: {source.path}")

    payload = json.loads(source_path.read_text(encoding="utf-8"))
    items = payload["questions"] if isinstance(payload, dict) and "questions" in payload else payload
    if not isinstance(items, list):
        raise ValueError(f"Local source '{source.name}' did not contain a list of questions.")

    results: list[ScrapedQuestion] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        prompt = str(item.get(source.prompt_field, "")).strip()
        if len(prompt) < source.min_length:
            continue
        if source.require_question_mark and "?" not in prompt:
            continue

        metadata = {key: value for key, value in item.items() if key != source.prompt_field}
        results.append(
            ScrapedQuestion(
                prompt=prompt,
                category=source.category,
                source_name=source.name,
                source_url=source.url or f"local://{source.path}",
                metadata=metadata,
            )
        )

        if len(results) >= source.max_items:
            break

    return results
