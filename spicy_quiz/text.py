from __future__ import annotations

import re


LEADING_NUMBER_RE = re.compile(r"^\s*(?:\d+[\).\:-]\s*|[-*•]\s*)")
NUMBERED_SPLIT_RE = re.compile(r"(?=(?:^|\s)\d+[\).\:-]\s*)")
WHITESPACE_RE = re.compile(r"\s+")


def normalize_question_text(text: str, strip_prefixes: tuple[str, ...] = ()) -> str:
    cleaned = WHITESPACE_RE.sub(" ", text).strip()
    cleaned = LEADING_NUMBER_RE.sub("", cleaned)

    for prefix in strip_prefixes:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix) :].strip()
            break

    return cleaned


def extract_question_candidates(
    text: str,
    strip_prefixes: tuple[str, ...] = (),
    numbered_only: bool = False,
) -> list[str]:
    cleaned = WHITESPACE_RE.sub(" ", text).strip()
    if not cleaned:
        return []

    has_numbered_items = bool(NUMBERED_SPLIT_RE.search(cleaned))
    if numbered_only and not has_numbered_items:
        return []

    if has_numbered_items:
        parts = [part.strip() for part in NUMBERED_SPLIT_RE.split(cleaned) if part.strip()]
    else:
        parts = [cleaned]

    return [normalize_question_text(part, strip_prefixes) for part in parts if part.strip()]
