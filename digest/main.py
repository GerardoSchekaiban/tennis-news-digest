"""Run the whole pipeline once:  python -m digest.main

Each step is added in its milestone. Uncomment as you go.
"""

from pathlib import Path

import yaml
from digest import db

from digest.sources import youtube, rss


def run():
    config = yaml.safe_load(Path("config/sources.yaml").read_text())

    # 1. fetch (milestones 1 and 5)
    #articles = youtube.fetch(config.get("youtube", []))
    articles = rss.fetch(config.get("rss", []))
    print(f"fetched {len(articles)} articles")

    # 2. store       (milestone 2)  db.save_articles(...)
    with db.connect() as conn:
        stored = db.save_articles(conn, articles)
        print(f"stored {stored} new articles")

    # 3. summarize   (milestones 3-4)
    # 4. dedup       (milestone 6)
    # 5. rank        (milestone 7)
    # 6. compose + email (milestone 8)


if __name__ == "__main__":
    run()
