"""Database access. MILESTONE 2.

TODO:


- connect(): open a psycopg connection from DATABASE_URL (python-dotenv loads .env)
- save_articles(conn, articles): insert, ignoring ones already stored
  (hint: INSERT ... ON CONFLICT DO NOTHING)
- unsummarized(conn): articles that don't have Claude's output yet (milestone 3/4)
- later: save_summary, save_embedding, recent_embeddings
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()  # read .env once, when this file is first imported


def connect() -> psycopg.Connection:
    """Open a connection to the database in DATABASE_URL."""
    url = os.environ["DATABASE_URL"]
    conn = psycopg.connect(url)
    return conn

from digest.models import Article
from psycopg.types.json import Jsonb


def save_articles(conn, articles: list[Article]) -> int:
    """Insert articles into the database, ignoring duplicates."""
    with conn.cursor() as cur:
        counter = 0
        for article in articles:
            cur.execute(
                """
                INSERT INTO articles (source, url, title, published_at, content_md, kind, extra)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                (
                    article.source,
                    article.url,
                    article.title,
                    article.published_at,
                    article.content_md,
                    article.kind,
                    #Send Python dict to Postgres as JSONB using psycopg's Jsonb wrapper
                    (Jsonb({"extra": article.extra})),
                ),
            )
            counter += cur.rowcount
    conn.commit()
    return counter