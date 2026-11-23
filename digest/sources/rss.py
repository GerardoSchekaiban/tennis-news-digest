"""RSS source: tennis news sites. MILESTONE 1.
python -m digest.sources.rss
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import trafilatura
import yaml

from digest.models import Article


def get_full_text(url: str) -> str | None:
    """Download a page and return its main text as Markdown.
    Return None if the page can't be downloaded or has no text."""

    html = trafilatura.fetch_url(url)
    if html is None:
        return None
    
    text = trafilatura.extract(html, output_format="markdown")
    return text


def fetch_feed(name: str, url: str, since: datetime) -> list[Article]:
    """Articles for one RSS feed published after `since`."""

    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        published = entry.get("published_parsed")

        if published:
            published_dt = datetime(*published[:6], tzinfo=timezone.utc) 
        else:
            published_dt = None
            
        if published_dt and published_dt < since:
            continue

        text = get_full_text(entry.link)

        if text is None:
            text = entry.get("summary", "")

        articles.append(
            Article(
                source=f"rss:{name}",
                url=entry.link,
                title=entry.title,
                published_at=published_dt,
                content_md=text,
                kind="article",
                extra={"feed": name},
            )
        )
    return articles


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
