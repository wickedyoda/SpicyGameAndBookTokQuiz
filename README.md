# SpicyGameAndBookTokQuiz

A scraper/data repo that collects spicy trivia, spicy prompts, and BookTok-style questions, stores them locally, and exports manifest files for another Discord bot to consume.

## What this does

- Scrapes question text from public webpages using CSS selectors you configure.
- Imports tracked local JSON prompt lists alongside scraped web sources.
- Saves deduplicated prompts into a local SQLite database.
- Exports a stable manifest index at `manifests/index.json`.
- Provides a CLI for refresh, export, category listing, and random-question lookup.

## Important constraint

Only scrape sites you are allowed to scrape. Check each site's robots.txt, terms of use, and rate limits before adding it to `sources.json`.

## Setup

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the example scraper config.

```bash
cp sources.example.json sources.json
```

3. `sources.example.json` already includes Twinfluence as the first configured source. Edit `sources.json` to add more sites or adjust selectors.

Optional environment variables:

- `SPICY_DB_PATH` defaults to `data/spicy_questions.sqlite3`
- `SPICY_EXPORT_PATH` defaults to `manifests/index.json`
- `SPICY_SOURCES_FILE` defaults to `sources.json`
- `SPICY_SCRAPER_USER_AGENT` overrides the user agent sent while scraping

## Source config format

Each source entry in `sources.json` looks like this:

```json
{
  "name": "twinfluence-dirty-truth",
  "source_type": "web",
  "url": "https://twinfluence.com/dirty-truth-questions/",
  "category": "dirty-truth",
  "question_selector": "article p",
  "min_length": 20,
  "max_items": 300,
  "require_question_mark": true,
  "numbered_only": true
}
```

Fields:

- `name`: unique source label shown in Discord
- `source_type`: `web` or `local-json`
- `url`: page to scrape
- `category`: grouping used by `!spicy`
- `question_selector`: CSS selector for the question elements
- `path`: local JSON file path for `local-json` sources
- `prompt_field`: field to read as the prompt for `local-json` sources
- `min_length`: skips short junk entries
- `max_items`: limits how many prompts are pulled from the page
- `require_question_mark`: only keeps prompts containing `?`
- `numbered_only`: only keeps numbered question blocks and splits merged numbered questions
- `strip_prefixes`: removes common labels like `Q:` before saving

## CLI usage

```bash
python3 scrape.py refresh
python3 scrape.py refresh --source twinfluence-dirty-truth
python3 scrape.py categories
python3 scrape.py random
python3 scrape.py random --category dirty-truth
python3 scrape.py export
```

Default behavior:

- `python3 scrape.py` behaves like `python3 scrape.py refresh`
- `refresh` scrapes configured sites and then regenerates `manifests/index.json` and sibling manifest files
- `random` prints a single question as JSON so your bot can shell out if needed

## Export format

The exported manifest index at `manifests/index.json` contains:

- `generated_at`
- `question_count`
- `categories`
- `category_counts`
- `source_counts`
- `files`

`files` points to additional JSON files in the same `manifests/` directory:

- `questions.all.json`
- one `category.*.json` file per category
- one `source.*.json` file per source

Each question object inside those files looks like this:

```json
{
  "prompt": "If I gave you a free pass to hook up with one celebrity, who would it be and why?",
  "category": "dirty-truth",
  "source_name": "twinfluence-dirty-truth",
  "source_url": "https://twinfluence.com/dirty-truth-questions/",
  "metadata": {}
}
```

Your Discord bot can either:

- read `manifests/index.json` and the referenced sibling files
- read `data/spicy_questions.sqlite3` directly
- shell out to `python3 scrape.py random --category dirty-truth`

## Project layout

- `scrape.py`: top-level scrape entrypoint
- `spicy_quiz/`: scraper, export, service, and storage code
- `sources.example.json`: example source config
- `sources.json`: active source config
- `local_sources/`: tracked manual prompt lists
- `data/`: generated SQLite database
- `manifests/`: generated manifest index and question shards
