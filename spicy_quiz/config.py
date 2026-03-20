from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_DB_PATH = Path("data/spicy_questions.sqlite3")
DEFAULT_EXPORT_PATH = Path("data/questions.json")
DEFAULT_SOURCES_PATH = Path("sources.json")


@dataclass(frozen=True)
class SourceConfig:
    name: str
    category: str
    url: str = ""
    question_selector: str = ""
    source_type: str = "web"
    path: str = ""
    prompt_field: str = "question"
    min_length: int = 12
    max_items: int = 100
    require_question_mark: bool = False
    numbered_only: bool = False
    strip_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AppConfig:
    db_path: Path
    export_path: Path
    sources_path: Path
    user_agent: str


@dataclass(frozen=True)
class SourcesFile:
    user_agent: str
    sources: tuple[SourceConfig, ...] = field(default_factory=tuple)


def load_app_config() -> AppConfig:
    db_path = Path(os.getenv("SPICY_DB_PATH", str(DEFAULT_DB_PATH)))
    export_path = Path(os.getenv("SPICY_EXPORT_PATH", str(DEFAULT_EXPORT_PATH)))
    sources_path = Path(os.getenv("SPICY_SOURCES_FILE", str(DEFAULT_SOURCES_PATH)))
    user_agent = os.getenv(
        "SPICY_SCRAPER_USER_AGENT",
        "SpicyGameAndBookTokQuizBot/0.1 (+set-your-contact-info)",
    ).strip()
    return AppConfig(
        db_path=db_path,
        export_path=export_path,
        sources_path=sources_path,
        user_agent=user_agent,
    )


def load_sources_file(path: Path, default_user_agent: str) -> SourcesFile:
    if not path.exists():
        raise FileNotFoundError(
            f"Sources config not found at {path}. Copy sources.example.json to sources.json first."
        )

    raw = json.loads(path.read_text(encoding="utf-8"))
    base_dir = path.parent
    sources = raw.get("sources", [])
    configs = []

    for item in sources:
        source_type = str(item.get("source_type", "web")).strip() or "web"
        local_path = str(item.get("path", "")).strip()
        if local_path:
            resolved_path = Path(local_path)
            if not resolved_path.is_absolute():
                local_path = str((base_dir / resolved_path).resolve())
        configs.append(
            SourceConfig(
                name=str(item["name"]).strip(),
                category=str(item["category"]).strip(),
                url=str(item.get("url", "")).strip(),
                question_selector=str(item.get("question_selector", "")).strip(),
                source_type=source_type,
                path=local_path,
                prompt_field=str(item.get("prompt_field", "question")).strip() or "question",
                min_length=int(item.get("min_length", 12)),
                max_items=int(item.get("max_items", 100)),
                require_question_mark=bool(item.get("require_question_mark", False)),
                numbered_only=bool(item.get("numbered_only", False)),
                strip_prefixes=tuple(str(value) for value in item.get("strip_prefixes", [])),
            )
        )

    return SourcesFile(
        user_agent=str(raw.get("user_agent", default_user_agent)).strip() or default_user_agent,
        sources=tuple(configs),
    )
