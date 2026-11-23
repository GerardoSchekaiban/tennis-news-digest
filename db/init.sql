-- Runs once, the first time the Postgres container starts with an empty volume.
-- To re-run it: docker compose down -v && docker compose up -d

CREATE EXTENSION IF NOT EXISTS vector;

-- TODO (milestone 2): create an `articles` table that can hold every field of
-- digest.models.Article. Think about:
--   * which column makes an article unique (so re-running the fetch doesn't duplicate rows)
--   * a JSONB column for Claude's structured output (milestone 4)
--   * a vector(N) column for embeddings (milestone 6); N depends on the embedding model
--   * timestamps: when it was published vs. when you fetched it

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    content_md TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'article',
    summary JSONB,
    extra JSONB
);
