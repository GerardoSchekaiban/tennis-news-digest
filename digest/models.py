"""The shared shape every source returns.

Every source module (rss.py, youtube.py, later scrapers) turns its raw data into
a list of Article objects. The rest of the pipeline only ever sees Article, so it
doesn't care where the content came from.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    source: str            # e.g. "rss:atp-news" or "youtube:Tennis TV"
    url: str               # canonical link; good candidate for a unique key
    title: str
    published_at: datetime | None
    content_md: str        # full text as Markdown (article body or video transcript)
    kind: str = "article"  # "article" or "video"
    extra: dict = field(default_factory=dict)  # anything source-specific
