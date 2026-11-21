"""YouTube source: recent videos from tennis channels, with their transcripts.

This module is a complete, working example. Read it before writing rss.py:
the RSS source follows exactly the same pattern.

How it works
1. Every YouTube channel publishes a free RSS feed of its latest ~15 videos at
   https://www.youtube.com/feeds/videos.xml?channel_id=<ID>. No API key needed.
2. feedparser reads that feed. Each entry carries the video id (`yt_videoid`).
3. youtube-transcript-api downloads the captions (auto-generated or manual).
4. We join the caption snippets into one text and wrap it in an Article.

"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

from digest.models import Article

FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def _published(entry) -> datetime | None:
    # feedparser gives a time.struct_time in UTC; turn it into an aware datetime.
    # Use .get to avoid KeyError if the entry has no published date.
    parsed = entry.get("published_parsed")

    #slice the first 6 elements of the parsed time tuple to get year, month, day, hour, minute, second
    return datetime(*parsed[:6], tzinfo=timezone.utc) if parsed else None


def get_transcript(video_id: str, languages=("en",)) -> str | None:
    """Return the video's transcript as plain text, or None if it has none."""
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    except CouldNotRetrieveTranscript as exc:
        # Covers: captions disabled, no transcript in these languages,
        # video unavailable, rate limited. Skipping is the right call here.
        print(f"[youtube] {video_id}: {type(exc).__name__}")
        return None
    return " ".join(snippet.text for snippet in fetched)


def fetch_channel(name: str, channel_id: str, since: datetime) -> list[Article]:
    """Articles for one channel's videos published after `since`."""
    feed = feedparser.parse(FEED_URL.format(channel_id=channel_id))
    articles = []
    for entry in feed.entries:
        published = _published(entry)
        if published and published < since:
            continue
        # Shorts usually have no useful transcript; skip them.
        if "/shorts/" in entry.link:
            continue
        transcript = get_transcript(entry.yt_videoid)
        if not transcript:
            continue
        articles.append(
            Article(
                source=f"youtube:{name}",
                url=entry.link,
                title=entry.title,
                published_at=published,
                content_md=f"# {entry.title}\n\n{transcript}",
                kind="video",
                extra={"video_id": entry.yt_videoid, "channel": name},
            )
        )
    return articles


def fetch(channels: list[dict], hours: int = 24) -> list[Article]:
    """Articles from every configured channel in the last 24 hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles = []
    for ch in channels:
        try:
            articles.extend(fetch_channel(ch["name"], ch["channel_id"], since))
        except Exception as exc:  # one broken channel shouldn't stop the run
            print(f"[youtube] {ch['name']}: {exc}")
    return articles


if __name__ == "__main__":
    config = yaml.safe_load(Path("config/sources.yaml").read_text())
    for a in fetch(config.get("youtube", []), hours=72):
        print(f"{a.published_at:%Y-%m-%d}  {a.source}  {a.title}")
        print(f"   {a.content_md[:200]!r}...\n")
