"""RSS source: tennis news sites. MILESTONE 1.

Follow the pattern in youtube.py. The skeleton is here; fill in the TODOs.

Try it:  python -m digest.sources.rss
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import trafilatura
import yaml

from digest.models import Article


def get_full_text(url: str) -> str | None:
    """Download a page and return its main text as Markdown.

    TODO: use trafilatura. Look at trafilatura.fetch_url and trafilatura.extract
    (check the `output_format` parameter). Return None when extraction fails.
    """
    raise NotImplementedError


def fetch_feed(name: str, url: str, since: datetime) -> list[Article]:
    """Articles from one feed published after `since`.

    TODO:
    - parse the feed with feedparser (see youtube.py)
    - skip entries older than `since`
    - get the full text; if that fails, fall back to the entry's summary
    - build and return Article objects
    """
    raise NotImplementedError


def fetch(feeds: list[dict], hours: int = 24) -> list[Article]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles = []
    for f in feeds:
        try:
            articles.extend(fetch_feed(f["name"], f["url"], since))
        except Exception as exc:
            print(f"[rss] {f['name']}: {exc}")
    return articles


if __name__ == "__main__":
    config = yaml.safe_load(Path("config/sources.yaml").read_text())
    for a in fetch(config.get("rss", [])):
        print(f"{a.published_at}  {a.source}  {a.title}")
