from __future__ import annotations

from pathlib import Path

from spicy_quiz.config import SourcesFile
from spicy_quiz.exporter import export_questions
from spicy_quiz.local_source import load_local_json_source
from spicy_quiz.scraper import scrape_source
from spicy_quiz.store import QuestionStore


class SpicyQuizService:
    def __init__(self, store: QuestionStore, sources_file: SourcesFile) -> None:
        self.store = store
        self.sources_file = sources_file

    def refresh(self, source_name: str | None = None) -> tuple[int, list[str]]:
        total = 0
        touched_sources: list[str] = []

        for source in self.sources_file.sources:
            if source_name and source.name.lower() != source_name.lower():
                continue

            if source.source_type == "local-json":
                questions = load_local_json_source(source)
            else:
                questions = scrape_source(source, user_agent=self.sources_file.user_agent)
            total += self.store.upsert_questions(questions)
            touched_sources.append(source.name)

        if source_name and not touched_sources:
            raise ValueError(f"Unknown source '{source_name}'.")

        return total, touched_sources

    def export(self, export_path: Path) -> int:
        questions = self.store.list_questions()
        export_questions(export_path, questions)
        return len(questions)
