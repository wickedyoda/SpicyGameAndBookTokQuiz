from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _titleize_category(category: str) -> str:
    return str(category).replace("-", " ").replace("_", " ").title()


def _prompt_to_catalog_entry(question: ScrapedQuestion, ordinal: int) -> dict[str, object]:
    tags = question.metadata.get("tags", [])
    normalized_tags = [str(tag).strip().lower() for tag in tags if str(tag).strip()] if isinstance(tags, list) else []
    return {
        "id": f"{_slugify(question.category)}_{ordinal:04d}",
        "type": "prompt",
        "category": str(question.category).strip().lower() or "general",
        "rating": "18+",
        "text": question.prompt,
        "tags": normalized_tags,
        "enabled": True,
        "source_name": question.source_name,
        "source_url": question.source_url,
        "metadata": question.metadata,
    }


def export_questions(index_path: Path, questions: list[ScrapedQuestion]) -> None:
    manifest_dir = index_path.parent
    manifest_dir.mkdir(parents=True, exist_ok=True)

    for stale_file in manifest_dir.rglob("*.json"):
        stale_file.unlink()

    category_counts = Counter(question.category for question in questions)
    source_counts = Counter(question.source_name for question in questions)
    generated_at = datetime.now(timezone.utc).isoformat()
    packs_dir = manifest_dir / "packs"
    try:
        manifest_root = manifest_dir.relative_to(Path.cwd())
    except ValueError:
        manifest_root = Path(manifest_dir.name)
    prompts_by_category: dict[str, list[ScrapedQuestion]] = defaultdict(list)
    for question in questions:
        prompts_by_category[question.category].append(question)

    packs: list[dict[str, object]] = []
    for category in sorted(prompts_by_category):
        filename = _manifest_filename("pack", category)
        pack_path = str(manifest_root / "packs" / filename)
        pack_questions = prompts_by_category[category]
        pack_entries = [
            _prompt_to_catalog_entry(question, ordinal + 1)
            for ordinal, question in enumerate(pack_questions)
        ]
        pack_id = _slugify(category)
        pack_name = _titleize_category(category)
        _write_json(
            packs_dir / filename,
            {
                "id": pack_id,
                "name": pack_name,
                "generated_at": generated_at,
                "prompt_count": len(pack_entries),
                "prompts": pack_entries,
            },
        )
        packs.append(
            {
                "id": pack_id,
                "name": pack_name,
                "path": pack_path,
                "prompt_count": len(pack_entries),
                "enabled": True,
                "category": category,
            }
        )

    payload = {
        "generated_at": generated_at,
        "question_count": len(questions),
        "pack_count": len(packs),
        "categories": sorted(category_counts),
        "category_counts": dict(sorted(category_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "packs": packs,
    }

    _write_json(index_path, payload)
