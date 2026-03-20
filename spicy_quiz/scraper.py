from __future__ import annotations

from collections import OrderedDict

from spicy_quiz.config import SourceConfig
from spicy_quiz.models import ScrapedQuestion
from spicy_quiz.text import extract_question_candidates


class ScrapeError(RuntimeError):
    pass


BLOCKED_PAGE_MARKERS = (
    "please wait while your request is being verified",
    "cf-challenge",
    "cloudflare",
    "attention required!",
)


def scrape_source(source: SourceConfig, user_agent: str, timeout_seconds: int = 15) -> list[ScrapedQuestion]:
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(
        source.url,
        headers={"User-Agent": user_agent},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    lowered_body = response.text.lower()
    if any(marker in lowered_body for marker in BLOCKED_PAGE_MARKERS):
        raise ScrapeError(
            f"Source '{source.name}' appears to be behind an anti-bot or verification page."
        )

    soup = BeautifulSoup(response.text, "html.parser")
    nodes = soup.select(source.question_selector)

    if not nodes:
        raise ScrapeError(
            f"Selector '{source.question_selector}' matched no content for source '{source.name}'."
        )

    prompts = OrderedDict()
    for node in nodes:
        texts = extract_question_candidates(
            node.get_text(" ", strip=True),
            strip_prefixes=source.strip_prefixes,
            numbered_only=source.numbered_only,
        )
        for text in texts:
            if len(text) < source.min_length:
                continue
            if source.require_question_mark and "?" not in text:
                continue
            prompts[text] = None
            if len(prompts) >= source.max_items:
                break
        if len(prompts) >= source.max_items:
            break

    return [
        ScrapedQuestion(
            prompt=prompt,
            category=source.category,
            source_name=source.name,
            source_url=source.url,
        )
        for prompt in prompts
    ]
