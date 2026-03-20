from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from spicy_quiz.models import ScrapedQuestion


class QuestionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(questions)").fetchall()
            }
            if "metadata_json" not in columns:
                connection.execute(
                    "ALTER TABLE questions ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}'"
                )

    def upsert_questions(self, questions: list[ScrapedQuestion]) -> int:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.executemany(
                """
                INSERT INTO questions (prompt, category, source_name, source_url, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(prompt) DO UPDATE SET
                    category = excluded.category,
                    source_name = excluded.source_name,
                    source_url = excluded.source_url,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                [
                    (
                        question.prompt,
                        question.category,
                        question.source_name,
                        question.source_url,
                        json.dumps(question.metadata, ensure_ascii=True, sort_keys=True),
                    )
                    for question in questions
                ],
            )
            return cursor.rowcount if cursor.rowcount != -1 else len(questions)

    def get_random_question(self, category: str | None = None) -> ScrapedQuestion | None:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            params: tuple[str, ...] = ()
            query = """
                SELECT prompt, category, source_name, source_url
                     , metadata_json
                FROM questions
            """
            if category:
                query += " WHERE lower(category) = lower(?)"
                params = (category,)
            query += " ORDER BY RANDOM() LIMIT 1"
            row = connection.execute(query, params).fetchone()

        if row is None:
            return None

        return ScrapedQuestion(
            prompt=row["prompt"],
            category=row["category"],
            source_name=row["source_name"],
            source_url=row["source_url"],
            metadata=json.loads(row["metadata_json"] or "{}"),
        )

    def list_categories(self) -> list[str]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT DISTINCT category FROM questions ORDER BY category COLLATE NOCASE"
            ).fetchall()
        return [row[0] for row in rows]

    def list_questions(self, category: str | None = None) -> list[ScrapedQuestion]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            params: tuple[str, ...] = ()
            query = """
                SELECT prompt, category, source_name, source_url
                     , metadata_json
                FROM questions
            """
            if category:
                query += " WHERE lower(category) = lower(?)"
                params = (category,)
            query += " ORDER BY category COLLATE NOCASE, prompt COLLATE NOCASE"
            rows = connection.execute(query, params).fetchall()

        return [
            ScrapedQuestion(
                prompt=row["prompt"],
                category=row["category"],
                source_name=row["source_name"],
                source_url=row["source_url"],
                metadata=json.loads(row["metadata_json"] or "{}"),
            )
            for row in rows
        ]

    def count_questions(self) -> int:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute("SELECT COUNT(*) FROM questions").fetchone()
        return int(row[0]) if row else 0
