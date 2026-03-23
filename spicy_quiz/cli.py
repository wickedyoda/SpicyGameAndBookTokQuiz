from __future__ import annotations

import argparse
import json

from spicy_quiz.config import load_app_config, load_sources_file
from spicy_quiz.service import SpicyQuizService
from spicy_quiz.store import QuestionStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape and export spicy quiz data.")
    subparsers = parser.add_subparsers(dest="command")

    refresh_parser = subparsers.add_parser("refresh", help="Scrape configured sources and export manifests.")
    refresh_parser.add_argument("--source", help="Optional source name to refresh.")

    subparsers.add_parser("categories", help="List loaded categories.")

    random_parser = subparsers.add_parser("random", help="Print one random question as JSON.")
    random_parser.add_argument("--category", help="Optional category filter.")

    export_parser = subparsers.add_parser("export", help="Export the current SQLite data to manifests.")
    export_parser.add_argument("--category", help="Optional category filter for the exported payload.")

    args = parser.parse_args()

    config = load_app_config()
    sources_file = load_sources_file(config.sources_path, config.user_agent)
    store = QuestionStore(config.db_path)
    store.initialize()
    service = SpicyQuizService(store, sources_file)

    if args.command in (None, "refresh"):
        result = service.refresh(getattr(args, "source", None))
        exported = service.export(config.export_path)
        success_label = ", ".join(result["successful_sources"]) if result["successful_sources"] else "none"
        print(
            f"Saved {result['saved_count']} scraped rows from: {success_label}"
            f"\nExported {exported} total questions to {config.export_path}"
        )
        if result["failed_sources"]:
            print("\nFailed sources:")
            for item in result["failed_sources"]:
                print(f"- {item['name']}: {item['error']}")
        return

    if args.command == "categories":
        print(json.dumps(store.list_categories(), indent=2))
        return

    if args.command == "random":
        question = store.get_random_question(args.category)
        if question is None:
            raise SystemExit("No matching questions found.")
        print(json.dumps(question.to_dict(), indent=2))
        return

    if args.command == "export":
        if args.category:
            from spicy_quiz.exporter import export_questions

            questions = store.list_questions(args.category)
            export_questions(config.export_path, questions)
            print(
                f"Exported {len(questions)} questions for category '{args.category}'"
                f" to {config.export_path}"
            )
            return

        exported = service.export(config.export_path)
        print(f"Exported {exported} total questions to {config.export_path}")
